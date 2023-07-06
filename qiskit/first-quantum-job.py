import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import execute
from qiskit_iqm import IQMProvider

shots = 1000

qreg = QuantumRegister(2, "QB")
creg = ClassicalRegister(2, "C")
circuit = QuantumCircuit(qreg, creg)

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

job = execute(circuit, backend, shots=shots, initial_layout=qubit_mapping)
counts = job.result().get_counts()
print(counts)
