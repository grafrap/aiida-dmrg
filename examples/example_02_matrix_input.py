# pylint: disable=invalid-name
"""Run simple DFT calculation"""


import sys
from collections import OrderedDict

import click
from aiida.common import NotExistent
from aiida.engine import run_get_node
from aiida.orm import Dict, load_code
from aiida.plugins import CalculationFactory

DMRGCalculation = CalculationFactory("dmrg")


def example_dmrg(dmrg_code):
    """Run a simple dmrg calculation"""

    num_cores = 2
    memory_mb = 20000

    n_sites = 10
    val1, val2 = 23, 38

    matrix = [[0 for _ in range(n_sites)] for _ in range(n_sites)]

    for i in range(n_sites - 1):
        matrix[i][i + 1] = val1 if i % 2 == 0 else val2
        matrix[i + 1][i] = val1 if i % 2 == 0 else val2

    # Main parameters: dmrg input file
    parameters = Dict(
        dict=OrderedDict(
            [
                ("title", "DMRG calculation"),
                ("comment", "Example calculation"),
                ("S", 1),
                ("N_sites", n_sites),
                ("cutoff", 1e-8),
                ("J", matrix),
                ("n_excitations", 0),
                ("conserve_symmetry", "false"),
                ("print_HDF5", "true"),
                ("maximal_energy", "true"),
            ]
        )
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
    builder.metadata.options.max_wallclock_seconds = 20 * 60

    print("Running calculation...")
    res, _node = run_get_node(builder)

    print("Calculation finished with state: ", res)


@click.command("cli")
@click.argument("codelabel", default="dmrg@daint-mc-julia")
def cli(codelabel):
    """Click interface"""
    try:
        code = load_code(codelabel)
    except NotExistent:
        print(f"The code '{codelabel}' does not exist")
        sys.exit(1)
    example_dmrg(code)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
