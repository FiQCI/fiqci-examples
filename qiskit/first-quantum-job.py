import os

from qiskit import QuantumCircuit, QuantumRegister
from qiskit import execute
from qiskit_iqm import IQMProvider

shots = 1000

qreg = QuantumRegister(2, "QB")
circuit = QuantumCircuit(qreg, name='Bell pair circuit')

circuit.h(qreg[0])
circuit.cx(qreg[0], qreg[1])
circuit.measure_all()

# Uncomment if you wish to print the circuit
# print(circuit.draw())

# Qiskit uses 0 indexing for identifying qubits
qubit_mapping = {
    qreg[0]: 0,  # Map first qubit in Quantum Register to QB1
    qreg[1]: 2,  # Map second qubit in Quantum Register to QB3
}

HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
if not HELMI_CORTEX_URL:
    raise ValueError("Environment variable HELMI_CORTEX_URL is not set")

provider = IQMProvider(HELMI_CORTEX_URL)
backend = provider.get_backend()

# Retrieving backend information
# print(f'Native operations: {backend.operation_names}')
# print(f'Number of qubits: {backend.num_qubits}')
# print(f'Coupling map: {backend.coupling_map}')

job = execute(circuit, backend, shots=shots, initial_layout=qubit_mapping)
result = job.result()
exp_result = job.result()._get_experiment(circuit)
# You can retrieve the job at a later date with backend.retrieve_job(job_id)
# Uncomment the following lines to get more information about your submitted job
print("Job ID: ", job.job_id())
# print(result.request.circuits)
print("Calibration Set ID: ", exp_result.calibration_set_id)
# print(result.request.qubit_mapping)
# print(result.request.shots)

counts = result.get_counts()
print(counts)
