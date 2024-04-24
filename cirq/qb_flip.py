"""
A more advanced example to flip qubits with either Helmi or the simulator.
"""
import argparse
import os
from argparse import RawTextHelpFormatter

import numpy as np
from iqm.cirq_iqm.iqm_sampler import IQMSampler

import cirq


def fold_func(x: np.ndarray) -> str:
    """Fold the measured bit arrays into strings."""
    return ''.join(map(lambda x: chr(x + ord('0')), x))


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


def single_flip_circuit(qubit: int):
    """
    Returns a 1-qubit circuit with an X gate to flip the qubit from |0> to |1>.
    Also returns the correct mapping.
    """
    qubit = cirq.NamedQubit(f'QB{qubit}')
    circuit = cirq.Circuit()
    circuit.append(cirq.X(qubit))
    circuit.append(cirq.measure(qubit, key='M'))
    return circuit


def flip_circuit(qubits: list[int]):
    """
    Creates a quantum circuit with X gates applied to the qubits specified in the input list.
    """
    qubits = [cirq.NamedQubit(f'QB{i}') for i in qubits]
    circuit = cirq.Circuit()
    for qubit in qubits:
        circuit.append(cirq.X(qubit))
    circuit.append(cirq.measure(*qubits, key='M'))
    return circuit


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
        sampler = IQMSampler(HELMI_CORTEX_URL)
    else:
        sampler = cirq.Simulator()

    circuits = []
    if qubits is None:  # Flip all qubits
        print("Flipping all qubits")
        circuit = flip_circuit(list(range(1, 6)))
        circuits.append(circuit)
    else:  # Flip specified qubits
        print("Flipping qubits: ", qubits)
        for qb in qubits:
            circuit = single_flip_circuit(qb)
            circuits.append(circuit)

    for i, circuit in enumerate(circuits):
        if verbose:
            print(f"Circuit {i+1}:\n")
            print(circuit)

        result = sampler.run(circuit, repetitions=shots)

        counts = result.histogram(key='M', fold_func=fold_func)

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

    args = get_args()

    flip_qubits(args.qubits, args.backend, args.shots, args.verbose)


if __name__ == "__main__":
    main()
