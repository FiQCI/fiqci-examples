"""
Simple qubit flipping example
"""
import os
from qiskit import QuantumCircuit, QuantumRegister
from qiskit import execute
from qiskit_iqm import IQMProvider
from typing import List, Tuple


def single_flip_circuit(qubit: int) -> Tuple[QuantumCircuit, dict]:
    """
    Returns a 1-qubit circuit with an X gate to flip the qubit from |0> to |1>.
    Also returns the correct mapping.
    """
    qreg = QuantumRegister(1, "qb")
    qc = QuantumCircuit(qreg)
    qc.x(0)
    qc.measure_all()
    mapping = {qreg[0]: qubit}
    return qc, mapping


def flip_circuit(qubits: List[int]) -> Tuple[QuantumCircuit, dict]:
    """
    Creates a quantum circuit with X gates applied to the qubits specified in the input list.
    Returns the circuit and a mapping of qubits.
    """
    qreg = QuantumRegister(len(qubits), "qb")
    qc = QuantumCircuit(qreg)
    for qubit in qubits:
        qc.x(qubit)
    qc.measure_all()
    mapping = {qreg[i]: qubits[i] for i in range(len(qubits))}
    return qc, mapping


def calculate_success_probability(counts: dict, shots: int, desired_state: str) -> float:
    """
    Calculate the success probability from the job results.
    """
    success_counts = counts.get(desired_state, 0)
    return success_counts / shots


def main():

    HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
    if not HELMI_CORTEX_URL:
        raise ValueError("Environment variable HELMI_CORTEX_URL is not set")
    provider = IQMProvider(HELMI_CORTEX_URL)
    backend = provider.get_backend()

    shots = 1000

    print("\nFlip one qubit at a time\n")
    for qb in range(5):
        circuit, mapping = single_flip_circuit(qb)
        shots = 1000
        job = execute(circuit, backend, shots=shots, initial_layout=mapping)
        # assert that the mapping is correct
        assert 'QB'+str(qb+1) == job.result().request.qubit_mapping[0].physical_name
        counts = job.result().get_counts()
        success_probability = calculate_success_probability(counts, shots, '1')
        print(f"QB{qb + 1} -> {counts}, Success probability: {success_probability * 100:.2f}%")

    print("\nFlip all qubits at once\n")
    circuit, mapping = flip_circuit([0, 1, 2, 3, 4])
    job = execute(circuit, backend, shots=shots, initial_layout=mapping)
    counts = job.result().get_counts()
    success_probability = calculate_success_probability(counts, shots, '11111')
    print(f"Counts: {counts}, \nSuccess probability: {success_probability * 100:.2f}%")


if __name__ == "__main__":
    main()
