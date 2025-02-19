"""Tests for the Dyncorr calculation class."""

from collections import OrderedDict
from copy import copy

from aiida.orm import Dict

from aiida_dmrg.calculations.dyncorr_calc import DynCorrCalculation


def test_dmrg_calculation_default(
    fixture_code,
    generate_calc_job,
    fixture_remote_data,
):
    """Test a default calculation for :class.
    `aiida_dmrg.calculations.dyncorr_calc.DyncorrCalculation`.
    """

    memory_mb = 6000

    dyncorr_parameters1 = Dict(
        dict=OrderedDict(
            [
                ("title", "Dyncorr calculation"),
                ("comment", "Example calculation"),
                ("E_range", 2),
                ("N", 2000),
                ("num_points", 1000),
            ]
        )
    )

    dyncorr_parameters2 = Dict(
        dict=OrderedDict(
            [
                ("title", "Dyncorr calculation"),
                ("comment", "Example calculation"),
                ("E_range", 2),
                ("num_points", 2000),
            ]
        )
    )

    inputs1 = {
        "code": fixture_code("dyncorr"),
        # load_code("dyncorr@daint-mc-julia"),
        "parameters": dyncorr_parameters1,
        "parent_calc_folder": fixture_remote_data,
        "metadata": {
            "options": {
                "resources": {
                    "num_machines": 1,
                    "num_mpiprocs_per_machine": 1,
                    "num_cores_per_mpiproc": 8,
                },
                "max_memory_kb": int(1.25 * memory_mb) * 1024,
                "max_wallclock_seconds": 5 * 60,
            },
        },
    }

    inputs2 = copy(inputs1)
    inputs2["parameters"] = dyncorr_parameters2

    expected_content1 = "2 1000 2000"

    expected_content2 = "2 2000"

    for inputs, expected_content in [
        (inputs1, expected_content1),
        (inputs2, expected_content2),
    ]:
        tmp_dir, _ = generate_calc_job(DynCorrCalculation, inputs)
        input_file_path = tmp_dir / DynCorrCalculation.INPUT_FILE
        content_input_file = input_file_path.read_text()
        print("content of the output:", content_input_file.strip())

        assert content_input_file.strip() == expected_content
