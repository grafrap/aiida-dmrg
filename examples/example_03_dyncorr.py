# pylint: disable=invalid-name
"""Run DMRG calculation followed by dynamic correlator"""

import sys
from collections import OrderedDict

import click
from aiida.common import NotExistent
from aiida.engine import run_get_node
from aiida.orm import Code, Dict, load_code
from aiida.plugins import CalculationFactory, WorkflowFactory

DynCorrWorkChain = WorkflowFactory('dyncorr.base')

def example_dyncorr(code):
    """Run DMRG followed by dynamic correlator calculation"""
    
    num_cores = 2
    memory_mb = 6000

    # DMRG parameters
    dmrg_parameters = Dict(dict=OrderedDict([
        ("title", "DMRG calculation"),
        ("comment", "Example calculation"),
        ("S", 1),
        ("N_sites", 8),
        ("J", 2),
        ("Sz", 0),
        ("n_excitations", 0),
        ("conserve_symmetry", "false"),
        ("print_HDF5", "true"),
    ]))

    # Build workflow inputs
    inputs = {
        'dmrg': {
            'parameters': dmrg_parameters,
            'code': code,
            'metadata': {
                'options': {
                    'withmpi': True,
                    'resources': {
                        'num_machines': 1,
                        'tot_num_mpiprocs': num_cores,
                    },
                    'max_memory_kb': int(1.25 * memory_mb) * 1024,
                    'max_wallclock_seconds': 5 * 60,
                }
            }
        },
        'dyncorr': {
            'code': code,  # Using same code for both calculations
            'metadata': {
                'options': {
                    'withmpi': True,
                    'resources': {
                        'num_machines': 1,
                        'tot_num_mpiprocs': num_cores,
                    },
                    'max_memory_kb': int(1.25 * memory_mb) * 1024,
                    'max_wallclock_seconds': 5 * 60,
                }
            }
        }
    }

    print("Running calculations...")
    res, node = run_get_node(DynCorrWorkChain, **inputs)

    print("DMRG results: ", res.dmrg_output_parameters)
    print("Dynamic correlator results: ", res.dyncorr_output_parameters)


@click.command("cli")
@click.argument("codelabel", default="dmrg@daint-mc-julia")
def cli(codelabel):
    """Click interface"""
    try:
        code = load_code(codelabel)
    except NotExistent:
        print(f"The code '{codelabel}' does not exist")
        sys.exit(1)
    example_dyncorr(code)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter