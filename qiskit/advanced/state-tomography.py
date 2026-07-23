"""
NOTE: This script is using qiskit-experiments 0.14.

On LUMI you can install it after loading the fiqci-vtt-qiskit module with the following command:
pip install --user qiskit-experiments==0.14

An example of using the Qiskit experiments library on Q50

The StateTomography experiment creates a single job containing several circuits.
As part of the analysis, the experiment estimates the density matrix of the state based on the results.

Additional details on Qiskit Experiments can be found here: https://qiskit.org/ecosystem/experiments/ and
more info on the StateTomography experiment can be found here:
https://github.com/qiskit-community/qiskit-experiments/blob/0.14/docs/manuals/verification/state_tomography.rst
"""

import os

from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.fake_backends import IQMFakeAdonis
from qiskit_experiments.library import StateTomography

from qiskit import QuantumCircuit
from qiskit.visualization import plot_state_city

backend = IQMFakeAdonis()

# Set up the Q50 backend
Q50_CORTEX_URL = os.getenv('Q50_CORTEX_URL')
if not Q50_CORTEX_URL:
    print("Environment variable Q50_CORTEX_URL is not set. Are you running on Lumi? Falling back to a simulator.")
    # raise ValueError("Environment variable Q50_CORTEX_URL is not set")

else:
    provider = IQMProvider(Q50_CORTEX_URL)
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
).block_for_results()
jobs = tomography_data.jobs()
print(jobs)
print(jobs[0].status())


# As of qiskit-experiments 0.9, analysis_results() returns a pandas DataFrame
# when dataframe=True (the implicit single-result return is deprecated).
state_result = tomography_data.analysis_results("state", dataframe=True).iloc[0]
print(state_result)
plot_state_city(
    state_result.value, title="Density Matrix",
    filename="density_matrix.png",
)
