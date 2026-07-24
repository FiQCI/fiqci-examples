"""
This example demonstrates how to get metadata about your job submitted with Qiskit
"""
import os

from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.fake_backends import IQMFakeAdonis

from qiskit import QuantumCircuit, transpile

backend = IQMFakeAdonis()

# Set up the Q50 backend
Q50_CORTEX_URL = os.getenv('Q50_CORTEX_URL')
if not Q50_CORTEX_URL:
    print("Environment variable Q50_CORTEX_URL is not set. Are you running on Lumi? Falling back to a simulator.")
    # raise ValueError("Environment variable Q50_CORTEX_URL is not set")

else:
    provider = IQMProvider(Q50_CORTEX_URL, quantum_computer="q50")
    backend = provider.get_backend()

# Retrieving backend information
print(f'Native operations: {backend.operation_names}')
print(f'Number of qubits: {backend.num_qubits}')
print(f'Coupling map: {backend.coupling_map}')

# Example Bell Pair circuit

circuit = QuantumCircuit(2, name='Bell pair circuit')
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

print(circuit.draw(output='text'))

# Explicitly transpiling the circuit allows us to access
# more information about the circuit that will be submitted

circuit_transpiled = transpile(
    circuit, backend=backend, layout_method='sabre', optimization_level=3,
)
print(circuit_transpiled.draw(output='text'))

mapping = {}
for qubit in circuit_transpiled.qubits:
    index = circuit_transpiled.find_bit(qubit).index
    mapping[index] = backend.index_to_qubit_name(index)

print(mapping)


job = backend.run(circuit_transpiled, shots=100)
result = job.result()
exp_result = result._get_experiment()

print("Job ID: ", job.job_id(), end="\n")  # Retrieving the submitted job id

# Retrieving the circuit request sent
print("Circuits: ", job._iqm_job._circuits[0], end="\n")
print(
    "Mapping: ", job._iqm_job._parameters.qubit_mapping,
)
print("Calibration Set ID: ", exp_result.calibration_set_id, end="\n")

# Retrieving the number of requested shots.
print("Shots: ", exp_result.shots, end="\n")

# retrieve a job using the job_id from a previous session
# old_job = backend.retrieve_job(job_id)
