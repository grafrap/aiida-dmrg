# aiida-dmrg

AiiDA plugin for the [DMRG software](https://github.com/grafrap/DMRG_Bachelor-Arbeit)

## Features

DMRG input can be provided as a aiida.orm Dict
```python
dmrg_parameters = Dict(dict=OrderedDict([
        ("title", "DMRG calculation"),
        ("comment", "Example calculation"),
        ("S", 1),
        ("cutoff", 1e-6),
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
        ("E_range", 2),
        ("num_points", 1000),
        ("N", 600),
    ]))
```

If J is given in meV, the `E_range` argument can usually be set to 2J of the corresponding DMRG calculation.\
`num_points` defines the number of $\omega$-values for the dynamical correlator between 0 and `E_range`.\
`N_max` is optional and gets calculated using an empirical formula if not provided. It defines the number of chebyshev expansion terms.

## Installation

```shell
pip install aiida-dmrg
```

This installs the plugins to the AiiDA instance (to double-check, one can list all installed plugins by `verdi plugin list aiida.calculations`).

## Usage
A quick demo of how to submit a calculation:
```shell
verdi daemon start # make sure the daemon is running
cd examples
# Submit test calculation (argument is the label of dmrg code)
verdi run example_01_simple.py dmrg
```
