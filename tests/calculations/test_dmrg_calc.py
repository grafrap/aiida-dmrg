"""Tests for the DMRG calculation class."""

from aiida.orm import Dict
from aiida_dmrg.calculations.dmrggen import DMRGCalculation
from collections import OrderedDict

def test_dmrg_calculation_default(fixture_code, generate_calc_job):
  """Test a default calculation for :class.`aiida_dmrg.calculations.dmrg.DmrgCalculation`."""

  num_cores = 1
  memory_mb = 6000

  parameters = Dict(dict=OrderedDict([
    ("title", "DMRG calculation"),
    ("comment", "Example calculation"),
    ("S", 0.5),
    ("N_sites", 8),
    ("J", 2),
    ("Sz", 0),
    ("n_excitations", 1), 
    ("conserve_symmetry", "false"),
    ("print_HDF5", "true"),
    ("maximal_energy", "true"),
  ]))
  
  inputs = {
    "code": fixture_code("dmrg"), # load_code("dmrg@daint-mc-julia"),
    "parameters": parameters,
    "metadata": {
      "options": {
        "resources": {
          "num_machines": 1,
          "tot_num_mpiprocs": num_cores,
        },
        "max_memory_kb": int(1.25 * memory_mb) * 1024,
        "max_wallclock_seconds": 5 * 60,
      },
    },
  }

  tmp_dir, _ = generate_calc_job(DMRGCalculation, inputs)
  input_file_path = tmp_dir / DMRGCalculation.INPUT_FILE 
  content_input_file = input_file_path.read_text()
  print("content of the output:",content_input_file.strip())

  expected_content = (
    "0.5 8 2 0 1 false true true"
  )
  assert content_input_file.strip() == expected_content
  
def test_dmrg_calculation_matrix(fixture_code, generate_calc_job):
  """Test a default calculation for :class.`aiida_dmrg.calculations.dmrg.DmrgCalculation`."""

  
  num_cores = 1
  memory_mb = 6000

  N = 4
  val1, val2 = 23, 38

  matrix = [[0 for _ in range(N)] for _ in range(N)]

  for i in range(N-1):
      matrix[i][i+1] = val1 if i % 2 == 0 else val2
      matrix[i+1][i] = val1 if i % 2 == 0 else val2

  parameters = Dict(dict=OrderedDict([
    ("title", "DMRG calculation"),
    ("comment", "Example calculation"),
    ("S", 1),
    ("N_sites", N),
    ("J", matrix),
    ("Sz", 0),
    ("n_excitations", 0), 
    ("conserve_symmetry", "false"),
    ("print_HDF5", "true"),
    ("maximal_energy", "true"),
  ]))
  
  inputs = {
    "code": fixture_code("dmrg"), # load_code("dmrg@daint-mc-julia"),
    "parameters": parameters,
    "metadata": {
      "options": {
        "resources": {
          "num_machines": 1,
          "tot_num_mpiprocs": num_cores,
        },
        "max_memory_kb": int(1.25 * memory_mb) * 1024,
        "max_wallclock_seconds": 5 * 60,
      },
    },
  }

  tmp_dir, _ = generate_calc_job(DMRGCalculation, inputs)
  input_file_path = tmp_dir / DMRGCalculation.INPUT_FILE 
  content_input_file = input_file_path.read_text()
  print("content of the output:",content_input_file.strip())

  expected_content = (
    "1 4 [[0, 23, 0, 0], [23, 0, 38, 0], [0, 38, 0, 23], [0, 0, 23, 0]] 0 0 false true true"
  )
  assert content_input_file.strip() == expected_content