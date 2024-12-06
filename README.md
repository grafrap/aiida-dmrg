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

For the J value, the input can also be a Julia or Python matrix of size `N_sites` x `N_sites`. An example for this can be found in `examples/example_02_matrix.py`. This matrix then represents the J_{ij} in the hamiltonian.

All the outputs of the calculation are stored in the `output_parameters` node. The HDF5 files of the hamiltonian, the wavefunction and the sites are stored on the node and have to be copied from the cluster, if one wants to use them.

To run the Dynamic Correlator workchain, one has to add some more parameters, also provided in an aiida.orm Dict
```Python
dyncorr_parameters = Dict(dict=OrderedDict([
        ("title", "Dynamic correlator calculation"),
        ("comment", "Example calculation"),
        ("J", 2),
        ("N_max", 2000),
        ("cutoff", 1e-6),
    ]))
```
Both `N_max` and `cutoff` are optional. If nothing is set, the default values are set as follows:
By default `N_max`, the number of chebyshev expansion coefficients, is set to the many-body bandwidth of the hamiltonian, i.e. the difference between minimal and maximal energy. If this default bandwidth falls below a threshold of 600 expansion coefficients, `N_max` gets set to 600.
By default `cutoff` is set to 1e-8. To get decent accuracy and still quite fast code, one should use a `cutoff` between 1e-8 and 1e-6.

J can be set also to a matrix, it just always has to be the same as the J of the corresponding DMRG calculation.
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
