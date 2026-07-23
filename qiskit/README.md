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

The `bell_states_qiskit.py` creates a `|00> + |11> / sqrt(2)` bell state between different qubit pairs and entangling them. This example is a good measure of how different qubit pairs interact and how utilising a devices topology gives better results. Each qubit pair (QB1&QB3 or QB2&QB3) contains one of the outer qubits (QB1, QB2, QB4, QB5) and the inner qubit QB3. The example creates a bell state by placing a hadamard gate on the outer qubit and a CNOT gate between the two qubits with a different control and target qubit each time. The example prints how often the correct bell state is measured and how often the `|00>` and `|11>` states exist, giving a mesure of noise.


### Bernstein Vazirani

The Bernstein-Vazirani algorithm attempts to solve the problem of finding some secret string that has been encoded by a black-box algorithm. In this example, the quantum version is implemented with a hidden oracle number randomly chosen and not disclosed. The quantum oracle function is created using hadamard and Z gates in a 5 qubit system to successfully find the hidden secret bit string after numerous attempts.


This example sends a 5 qubit circuit to Helmi, however the first 4 qubits are used for the algorithm. The 5th qubit here is used as an output qubit. `helmi.routing` is also utilised in this example.


### GHZ state

The GHZ example is a 5 qubit alternative to the bell state example. This time a bell state is between between one of the outer qubits and the inner qubit, QB3. The classical fidelity and trace distance is calculated for each qubit pair this time. The GHZ example finally prepares a 5 qubit GHZ state and efficiently maps this for Helmi's topology

```
           ┌───┐     ┌─┐
qB_0: ─────┤ X ├─────┤M├──────────────────────
           └─┬─┘┌───┐└╥┘     ┌─┐
qB_1: ───────┼──┤ X ├─╫──────┤M├──────────────
      ┌───┐  │  └─┬─┘ ║      └╥┘        ┌─┐
qB_2: ┤ H ├──■────■───╫───■───╫───■─────┤M├───
      └───┘           ║ ┌─┴─┐ ║   │  ┌─┐└╥┘
qB_3: ────────────────╫─┤ X ├─╫───┼──┤M├─╫────
                      ║ └───┘ ║ ┌─┴─┐└╥┘ ║ ┌─┐
qB_4: ────────────────╫───────╫─┤ X ├─╫──╫─┤M├
                      ║       ║ └───┘ ║  ║ └╥┘
 c: 5/════════════════╩═══════╩═══════╩══╩══╩═
                      0       1       3  2  4

```

2-Qubit gates are placed on QB3 (Here this is QB_2 due to Qiskit indexing starting from 0) with the target of one of the outer qubits. We can now measure the fidelity and trace distance for this.

- Fidelity is the "closeness" of two quantum states or how distinguishable they are from each other
    - For example a maximum value of 1 is attained if and only if the two states are identical.
    - For more detailed explanation have a look at: http://theory.caltech.edu/~preskill/ph219/chap2_15.pdf

- The "Distance from target" or the Trace Distance is the Quantum generalization of the "statistical distance"
    or Kolmogorov distance.
    It is another measure of the distinguishability between two quantum states


## Additional examples

Additional example can be found on the [Qiskit on IQM](https://iqm-finland.github.io/qiskit-on-iqm/user_guide.html) Website.
