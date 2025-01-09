import os

from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.fake_backends import IQMFakeAdonis

from qiskit import QuantumCircuit, QuantumRegister, transpile

shots = 1000

qreg = QuantumRegister(2, "QB")
circuit = QuantumCircuit(qreg, name='Bell pair circuit')

circuit.h(qreg[0])
circuit.cx(qreg[0], qreg[1])
circuit.measure_all()

# Uncomment if you wish to print the circuit
# print(circuit.draw())

# Set up the Helmi backend
backend = IQMFakeAdonis()
HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
if not HELMI_CORTEX_URL:
    print("""Environment variable HELMI_CORTEX_URL is not set.
          Are you running on Lumi and on the q_fiqci node?.
          Falling back to fake backend.""")
    # raise ValueError("Environment variable HELMI_CORTEX_URL is not set")

else:
    provider = IQMProvider(HELMI_CORTEX_URL)
    backend = provider.get_backend()
    circuit = transpile(
        circuit, backend, layout_method='sabre', optimization_level=3,
    )

# Retrieving backend information
# print(f'Native operations: {backend.operation_names}')
# print(f'Number of qubits: {backend.num_qubits}')
# print(f'Coupling map: {backend.coupling_map}')

job = backend.run(circuit, shots=shots)
result = job.result()
exp_result = job.result()._get_experiment(circuit)
# You can retrieve the job at a later date with backend.retrieve_job(job_id)
# Uncomment the following lines to get more information about your submitted job
print("Job ID: ", job.job_id())
"""
try:
    print(job.result().results[0].metadata['input_qubit_map'])
except AttributeError:
    print(job.result().request.qubit_mapping)
"""
# print(result.results[0].shots)

counts = result.get_counts()
print(counts)
