import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.compiler import transpile
import numpy as np
from csc_qu_tools.qiskit import Helmi

qreg = QuantumRegister(2, "qB")
creg = ClassicalRegister(2, "c")
circuit = QuantumCircuit(qreg, creg)

circuit.h(qreg[0])
circuit.cx(qreg[0], qreg[1])
circuit.measure(range(2), range(2))

# Uncomment if you wish to print the circuit
# print(circuit.draw())

basis_gates = ['r', 'cz']
circuit_decomposed = transpile(circuit, basis_gates=basis_gates)

# Uncomment if you wish to print the circuit
# print(circuit_decomposed.draw())

virtual_qubits = circuit_decomposed.qubits
qubit_mapping = {
                virtual_qubits[0]: "QB1",
                virtual_qubits[1]: "QB3",
            }

provider = Helmi()
backend = provider.set_backend()

job = backend.run(circuit_decomposed, shots=1000, qubit_mapping=qubit_mapping)

counts = job.result().get_counts()
print(counts)