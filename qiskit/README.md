# FiQCI Qiskit Examples

Examples made with Qiskit which are compatible with the FiQCI quantum computers (Aalto Q20 and VTT Q50). These examples were made with the aim to show how simple quantum jobs can be run on FiQCI devices and to demonstate the differences in results between the simulator and a real quantum computer. Therefore each example has the option to run with a simulator or with the Quantum Computer. Running jobs on an actual quantum computer requires submitting of jobs through the LUMI supercomputer. Alternatively one can access the quantum computers through the LUMI web interface, where it is possible to access them from a Jupyter notebook enviroment.

## Example list

| Example                                              | Code                    | Quick run                                      |
|------------------------------------------------------|-------------------------|------------------------------------------------|
| [Qubit Flipping]( #qubit-flipping)                   | `qb_flip.py`     | `python qb_flip.py --backend q50`     |
| [Bell State Entanglement]( #bell-state-entanglement) | `bell_states_qiskit.py` | `python bell_states_qiskit.py --backend q50` |
| [Bernstein Vazirani]( #bernstein-vazirani)           | `bv.py`                 | `python bernstein_vazirani.py --backend q50` |
| [GHZ state]( #ghz-state)                             | `ghz.py`                | `python ghz.py --backend q50`                |

All examples have command line arguments which can be viewed with the `-h` or `--help` option. You can run the scripts with the `-h` option in the LUMI login node. Using this also prints some example usage for each example. Each example also has the verbose option built in, add the `-v` or `--verbose` command line argument.

## Running on LUMI


To run these examples on LUMI you will need to:

- `module use /appl/local/quantum/modulefiles`
- `module load fiqci-vtt-qiskit`

Then jobs can be run through the batch queueing system, SLURM. Some example job submission bash scripts can be found in the `scripts` directory.

### Qubit Flipping

The Qubit flipping example, `qb_flip.py`, demonstrates simple qubit flipping. The example first flips the qubit state of each qubit (QB1, QB2,...) individually and reports the success rate which is how many out of the 10,000 counts are expected to be in the right state. The program then flips all the qubits at once in a 5 qubit circuit and reports the total success rate.

The `qb_flip_simple.py` is a simple version of the `qb_flip.py` code which runs with the default options.

### Bell State Entanglement

The `bell_state.ipynb` notebook demonstrates how to construct and execute a simple bell state circuit on VTT Q50.

### Bernstein Vazirani

The Bernstein-Vazirani algorithm attempts to solve the problem of finding some secret string that has been encoded by a black-box algorithm. In this example, the quantum version is implemented with a hidden oracle number randomly chosen and not disclosed. The quantum oracle function is created using hadamard and Z gates in a 5 qubit system to successfully find the hidden secret bit string after numerous attempts.


This example sends a 5 qubit circuit to the selected device, however the first 4 qubits are used for the algorithm. The 5th qubit here is used as an output qubit.


## Additional examples

Additional example can be found on the [Qiskit on IQM](https://iqm-finland.github.io/qiskit-on-iqm/user_guide.html) Website.
