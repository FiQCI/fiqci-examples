"""
A more advanced example to flip qubits with either Helmi or the simulator.
"""
import argparse
import os
from argparse import RawTextHelpFormatter

from qiskit_iqm import IQMProvider

from qiskit import Aer, QuantumCircuit, QuantumRegister, execute


def get_args():
    parser = argparse.ArgumentParser(
        description="Qubit flipping options", formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "--backend", choices=['helmi', 'simulator'],
        help="Backend to use: 'helmi' or 'simulator'", required=True,
    )
    parser.add_argument(
        "--qubits", type=int, nargs='+',
        help="List of qubits to flip. If not specified, will flip all qubits.",
    )
    parser.add_argument(
        "--shots", type=int, default=1000,
        help="Number of shots to run the circuit. Default is 1000.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output",
    )
    return parser.parse_args()


def calculate_success_probability(counts: dict, shots: int, desired_state: str) -> float:
    """
    Calculate the success probability from the job results.
    """
    success_counts = counts.get(desired_state, 0)
    return success_counts / shots


def flip_circuit(qubits: list[int]) -> tuple[QuantumCircuit, dict]:
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


def single_flip_circuit(qubit: int) -> tuple[QuantumCircuit, dict]:
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


def flip_qubits(qubits: list[int], backend: str, shots: int, verbose: bool):
    """
    Function to run the flip circuit
    """
    if backend == 'helmi':
        HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
        if not HELMI_CORTEX_URL:
            raise ValueError(
                "Environment variable HELMI_CORTEX_URL is not set",
            )
        provider = IQMProvider(HELMI_CORTEX_URL)
        backend = provider.get_backend()
    else:
        provider = Aer
        backend = provider.get_backend('aer_simulator')

    circuit_mapping_pairs = []  # circuit, mapping tuples
    if qubits is None:  # Flip all qubits
        print("Flipping all qubits")
        circuit, mapping = flip_circuit([0, 1, 2, 3, 4])
        circuit_mapping_pairs.append((circuit, mapping))
    else:  # Flip specified qubits
        print("Flipping qubits: ", qubits)
        for qb in qubits:
            circuit, mapping = single_flip_circuit(qb)
            circuit_mapping_pairs.append((circuit, mapping))

    # Calculate success probability
    for i, (circuit, mapping) in enumerate(circuit_mapping_pairs):
        if verbose:
            print(f"Circuit {i+1}:\n")
            print(circuit)

        job = execute(circuit, backend, shots=shots, initial_layout=mapping)
        counts = job.result().get_counts()

        if verbose and "IQM" in str(backend):
            print("Mapping")
            print(job.result().request.qubit_mapping)

        if qubits is None:
            success_probability = calculate_success_probability(
                counts, shots, '11111',
            )
        else:
            success_probability = calculate_success_probability(
                counts, shots, '1',
            )

        print("\nCounts:", counts)

        print(f"Success probability: {success_probability * 100:.2f}%")


def main():
    """
    Main function
    """
    args = get_args()

    flip_qubits(args.qubits, args.backend, args.shots, args.verbose)


if __name__ == "__main__":
    main()
