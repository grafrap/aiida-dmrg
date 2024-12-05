# aiida-dmrg

AiiDA plugin for the DMRG software

## Features

DMRG input can be provided as a aiida.orm Dict
```python
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
        ("maximal_energy", "true"),
    ]))
```
If `conserve_symmetry` is set to false, the `Sz` value will be ignored. In this case it doesn't have to be specified and can be left away.

All the outputs of the calculation are stored in the `output_parameters` node. The HDF5 files of the hamiltonian, the wavefunction and the sites are stored on the node and have to be copied from the cluster, if one wants to use them.

## Installation

```shell
pip install aiida-dmrg
```

This installs the plugins to the AiiDA instance(to double-check, one can list all installed plugins by `verdi plugin list aiida.calculations`). After this, the DMRG codes should be set up using the plugins (https://aiida.readthedocs.io/projects/aiida-core/en/latest/). TODO: change this link

## Usage
A quick demo of how to submit a calculation:
```shell
verdi daemon start # make sure the daemon is running
cd examples
# Submit test calculation (argument is the label of dmrg code)
verdi run example_01_simple.py dmrg
```

## For maintainers
TODO