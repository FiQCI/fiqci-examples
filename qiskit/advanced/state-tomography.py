"""
An example of using the Qiskit experiments library on Helmi
This example requires installing the qiskit-experiments package e.g,
python -m pip install qiskit-experiments

The StateTomography experiment creates a single job containing several circuits.
As part of the analysis, the experiment estimates the density matrix of the state based on the results.

This example does not show how to vizualize the results of the StateTomography experiment.

Additional details on Qiskit Experiments can be found here: https://qiskit.org/ecosystem/experiments/
"""
import os

from qiskit_experiments.library import StateTomography
from qiskit_iqm import IQMProvider

from qiskit import QuantumCircuit

HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
provider = IQMProvider(HELMI_CORTEX_URL)
backend = provider.get_backend()

circuit = QuantumCircuit(2, name='Bell pair circuit')
circuit.h(0)
circuit.cx(0, 1)

print(circuit.draw(output='text'))

tomography_circuit = StateTomography(circuit, physical_qubits=[0, 2])

# The circuit metadata can be printed like this
print(tomography_circuit.circuits()[0].metadata)


tomography_data = tomography_circuit.run(
    backend, seed_simulation=42, shots=100,
)
jobs = tomography_data.jobs()
print(jobs)
print(jobs[0].status())

tomography_data = tomography_data.block_for_results()
for result in tomography_data.analysis_results():
    print(result)
