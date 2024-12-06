"""Tests for the Dyncorr calculation class."""

from aiida.orm import Dict
from aiida_dmrg.calculations.dyncorr_calc import DynCorrCalculation
from collections import OrderedDict
from copy import copy

def test_dmrg_calculation_default(fixture_code, generate_calc_job, fixture_remote_data):
  """Test a default calculation for :class.`aiida_dmrg.calculations.dyncorr_calc.DyncorrCalculation`."""

  num_cores = 1
  memory_mb = 6000

  dyncorr_parameters1 = Dict(dict=OrderedDict([
    ("title", "Dyncorr calculation"),
    ("comment", "Example calculation"),
    ("J", 2),
    ("N_max", 2000),
    ("cutoff", 1e-6),
  ]))

  dyncorr_parameters2 = Dict(dict=OrderedDict([
    ("title", "Dyncorr calculation"),
    ("comment", "Example calculation"),
    ("J", 2),
    ("N_max", 2000),
  ]))

  dyncorr_parameters3 = Dict(dict=OrderedDict([
    ("title", "Dyncorr calculation"),
    ("comment", "Example calculation"),
    ("J", 2),
    ("cutoff", 1e-6),
  ]))

  dyncorr_parameters4 = Dict(dict=OrderedDict([
    ("title", "Dyncorr calculation"),
    ("comment", "Example calculation"),
    ("J", 2),
  ]))

  inputs1 = {
    "code": fixture_code("dyncorr"), # load_code("dyncorr@daint-mc-julia"),
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

  inputs3 = copy(inputs1)
  inputs3["parameters"] = dyncorr_parameters3

  inputs4 = copy(inputs1)
  inputs4["parameters"] = dyncorr_parameters4

  expected_content1 = (
    "2 2000 1e-06"
  )

  expected_content2 = (
    "2 2000"
  )

  expected_content3 = (
    "2 1e-06"
  )

  expected_content4 = (
    "2"
  )
  for inputs, expected_content in [(inputs1, expected_content1), (inputs2, expected_content2), (inputs3, expected_content3), (inputs4, expected_content4)]:
    tmp_dir, _ = generate_calc_job(DynCorrCalculation, inputs)
    input_file_path = tmp_dir / DynCorrCalculation.INPUT_FILE
    content_input_file = input_file_path.read_text()
    print("content of the output:",content_input_file.strip())

    assert content_input_file.strip() == expected_content