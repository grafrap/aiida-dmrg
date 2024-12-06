# pylint: disable=invalid-name
"""Run DMRG calculation followed by dynamic correlator"""

import sys
from collections import OrderedDict

import click
from aiida.common import NotExistent
from aiida.engine import run_get_node
from aiida.orm import Dict, load_code
from aiida.plugins import WorkflowFactory

DynCorrWorkChain = WorkflowFactory("dyncorr")


def example_dyncorr(code):
    """Run DMRG followed by dynamic correlator calculation"""

    num_cores = 2
    memory_mb = 30000

    # DMRG parameters
    dmrg_parameters = Dict(
        dict=OrderedDict(
            [
                ("title", "DMRG calculation"),
                ("comment", "Example calculation"),
                ("S", 1),
                ("N_sites", 8),
                ("J", 2),
                ("Sz", 0),
                ("n_excitations", 0),
                ("conserve_symmetry", "false"),
                ("print_HDF5", "true"),
                ("maximal_energy", "true"),
            ]
        )
    )

    dyncorr_parameters = Dict(
        dict=OrderedDict(
            [
                ("title", "Dynamic correlator calculation"),
                ("comment", "Example calculation"),
                ("J", 2),
                ("N_max", 200),
            ]
        )
    )

    builder = DynCorrWorkChain.get_builder()

    builder.dmrg_code = code
    builder.dyncorr_code = load_code(
        "dyncorr@daint-mc-julia"
    )  # TODO: Change to dyncorr@localhost
    builder.dmrg_params = dmrg_parameters
    builder.dyncorr_params = dyncorr_parameters
    builder.options = {
        "dmrg": {
            "withmpi": True,
            "resources": {
                "num_machines": 1,
                "num_mpiprocs_per_machine": num_cores,
                "num_cores_per_mpiproc": 1,
            },
            "max_wallclock_seconds": 3600,
            "max_memory_kb": memory_mb * 1024,
        },
        "dyncorr": {
            "resources": {
                "num_machines": 1,
                "num_mpiprocs_per_machine": 1,
                "num_cores_per_mpiproc": 8,  # num_cores,
            },
            "max_wallclock_seconds": 3600,
            "max_memory_kb": memory_mb * 1024,
        },
    }
    # builder.options = Dict(dict=options_dict)

    print("Running calculations...")
    res, node = run_get_node(builder)

    assert node.is_finished_ok


@click.command("cli")
@click.argument(
    "codelabel", default="dmrg@daint-mc-julia"
)  # TODO: change to dmrg@localhost
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
