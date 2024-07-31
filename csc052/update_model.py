#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from memote.suite.cli.reports import diff
import cobra
import os
import logging
from cobra.manipulation.modify import rename_genes
#from concerto.utils.biolog_help import add_biolog_exchanges
from cobra.io import read_sbml_model
import logging
import pandas as pd
import pathlib
import sys
import os
sys.path.insert(0, "/Users/rodr579/Repos/Concerto/concerto")
from concerto.utils import load_universal_model
##########
_log = logging.getLogger()

#_path = pathlib.Path(__file__).parent
_path = pathlib.Path(os.getcwd())
#_f_path = _path.joinpath('plate_to_bigg.csv').__str__()
_f_path = _path.joinpath('plate_to_bigg.csv').__str__()

starting_model = read_sbml_model("csc052.xml")

def write_model(model):
    cobra.io.write_sbml_model(model, output_model_path)


def update_1(model):
    
    """ Add missing BioLog exchanges to cobra model

    Adds missing BioLog exchanges from the plate to a cobra model. It grabs the
    reactions for the universal model, which should pull all annotations as
    well as metabolite information.


    Parameters
    ----------
    model : cobra.Model

    Returns
    -------
    cobra.Model
    """
    new_model = model.copy()
    not_found = set()
    added = set()

    # load in material needed to add biolog exchanges
    universal_model = load_universal_model()
    biolog_map = pd.read_csv(_f_path, index_col=False)

    for rxn in biolog_map.exchange:
        if rxn not in new_model.reactions:
            if rxn in universal_model.reactions:
                added.add(rxn)
                current_rxn = universal_model.reactions.get_by_id(rxn)
                metabolite = current_rxn.reactants[0]
                new_model.add_boundary(
                    metabolite,
                    type="exchange"
                )
            else:
                not_found.add(rxn)
    for i in not_found:
        _log.warning(f'{i} not found in universal model')
        print(f'{i} not found in universal model')
    _log.info(f"Added {len(added)} biolog exchange reactions")
    print(f"Added {len(added)} biolog exchange reactions")

    return new_model


def update_model():
    # Fix compartments
    model = update_1(starting_model)
    write_model(model)


if __name__ == '__main__':
    update_model()
    '''model_paths = [s_model_path, output_model_path]
    diff(
        [
            *model_paths,
            '--filename', os.path.join(_file_path, 'model_differences.html'),
            '--experimental', os.path.join(_file_path, 'data', 'experiments.yml'),
            # '--custom-tests', os.path.join(_file_path, 'custom_tests'),
            '--exclusive', 'test_growth',
        ]
    )'''


# In[ ]:




