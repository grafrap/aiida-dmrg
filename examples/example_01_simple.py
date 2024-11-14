# pylint: disable=invalid-name
"""Run simple DFT calculation"""


import sys

import ase.io
import click
from aiida.common import NotExistent
from aiida.engine import run_get_node
from aiida.orm import Code, Dict, StructureData
from aiida.plugins import CalculationFactory

DMRGCalculation = CalculationFactory("dmrg")


def example_dmrg(dmrg_code):
    """Run a simple dmrg calculation"""


    num_cores = 2
    memory_mb = 6000

    # Main parameters: dmrg input file
    parameters = Dict(
        {
            "link0_parameters": {
                "%chk": "aiida.chk",
                "%mem": "%dMB" % memory_mb,
                "%nprocshared": num_cores,
            },
            "S": 1,
            "N_sites": 8,
            "J": 1,
            "Sz": 0,
            "n_excitations": 0,
            "conserve_symmetry": False,
            "print_HDF5": True,
        }
    )

    # Construct process builder

    builder = DMRGCalculation.get_builder()

    builder.parameters = parameters
    builder.code = dmrg_code
    builder.metadata.options.withmpi = True

    builder.metadata.options.resources = {
        "num_machines": 1,
        "tot_num_mpiprocs": num_cores,
    }

    # Should ask for extra +25% extra memory
    builder.metadata.options.max_memory_kb = int(1.25 * memory_mb) * 1024
    builder.metadata.options.max_wallclock_seconds = 5 * 60

    print("Running calculation...")
    res, _node = run_get_node(builder)

    # print("Final scf energy: %.4f" % res["output_parameters"]["scfenergies"][-1])


@click.command("cli")
@click.argument("codelabel", default="dmrg@localhost")
def cli(codelabel):
    """Click interface"""
    try:
        code = Code.get_from_string(codelabel)
    except NotExistent:
        print(f"The code '{codelabel}' does not exist")
        sys.exit(1)
    example_dmrg(code)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
