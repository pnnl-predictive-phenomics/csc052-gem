#!/usr/bin/env bash

# Do NOT set -v or -x or your GitHub API token will be leaked!
#set -ue # exit with nonzero exit code if anything fails

echo "Parse memote.ini for values."
deployment=$(awk -F '=' '{if (! ($0 ~ /^;/) && $0 ~ /deployment/) print $2}' memote.ini | tr -d ' ')
location=$(awk -F '=' '{if (! ($0 ~ /^;/) && $0 ~ /location/) print $2}' memote.ini | tr -d ' ')

git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"
git config --global user.name "${GITHUB_ACTOR}"

echo "Deployment '${deployment}'"
echo "Location '${location}'"
echo "repository '${GITHUB_REPOSITORY}'"

if [[ "${GITHUB_EVENT_NAME}" == "pull_request" || "${GITHUB_REPOSITORY}" != "pnnl-predictive-phenomics/csc052-gem" ]]; then
    echo "Untracked build."
    memote run --ignore-git
		echo "Skip deploy."
    exit 0
else
		# Always need the deployment branch available locally for storing results.
		echo "Checking  if deployment branch ${deployment} is available"
		git checkout "${deployment}"
		echo "Back to base ${HEAD_REF}"
		git checkout ${HEAD_REF}
		echo "Tracked build."
		mkdir -p results
		memote run
		echo "Start deploy to ${deployment}..."
fi

# Generate a snapshot report on the deployment branch.
snapshot_output="snapshot_report.html"
git checkout "${deployment}"
echo "Generating snapshot report '${snapshot_output}'"
memote report snapshot --filename="${snapshot_output}"

# Generate the history report on the deployment branch.
output="history_report.html"
git checkout "${deployment}"
echo "Generating updated history report '${output}'."
memote report history --filename="${output}"

# Check if the report file exists
if [ -f "${output}" ]; then
  git add "${snapshot_output}"
  git add "${output}"
  git commit -m "Github actions report # ${GITHUB_SHA}"
  git push --quiet "https://github.com/${GITHUB_REPOSITORY}.git" "${deployment}" > /dev/null
  echo "Memote report was generated at https://pnnl-predictive-phenomics/${GITHUB_REPOSITORY}"
else
  echo "Error: Report file not found!"
  exit 1
fi
