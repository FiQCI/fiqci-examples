import os
import argparse
from argparse import RawTextHelpFormatter

import cirq
from cirq_iqm.iqm_sampler import IQMSampler
from cirq_iqm import Adonis
import numpy as np

"""

This example creates a 5 qubit GHZ stats in cirq

First a Bell state is prepared between QB3 and all the other qubits.
From this we can measure the trace distance between QB3 and each of the other qubits.

A 5 qubit GHZ state is then created 


"""

adonis = Adonis()


def get_args():

    args_parser = argparse.ArgumentParser(
        description="Single qubit flipping.", formatter_class=RawTextHelpFormatter
    )

    # Parse Arguments

    args_parser.add_argument(
        "--backend",
        help="""
        Define the backend for running the program.
        'simulator' runs on Cirq's Simulator, 
        'helmi' runs on VTT Helmi Quantum Computer
        """,
        required=True,
        type=str,
        default=None,
    )

    args_parser.add_argument(
        "--verbose",
        "-v",
        help="""
        Increase the output verbosity
        """,
        required=False,
        action="store_true",
    )

    return args_parser.parse_args()


def fold_func(x: np.ndarray) -> str:
    """Fold the measured bit arrays into strings."""
    return ''.join(map(lambda x: chr(x + ord('0')), x))


def main():
    offset = " " * 37
    offset_2 = " " * 10
    offset_3 = " " * 15

    args = get_args()

    if args.backend == 'helmi':
        HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
        if not HELMI_CORTEX_URL:
            raise ValueError("Environment variable HELMI_CORTEX_URL is not set")
        sampler = IQMSampler(HELMI_CORTEX_URL)
    else:
        sampler = cirq.Simulator()

    shots = 10000

    bell_vd = []
    id_dist = [0.5, 0, 0, 0.5]

    print(" ")
    print(offset + "================================ ")
    print(offset + "    Preparing a Bell State")
    print(offset + "================================ ")
    print(" ")
    count = 0
    for qb in [0, 1, 3, 4]:
        print(offset_2 + "QB" + str(qb + 1) + " and QB3 -> ", end=" ")
        q = [cirq.NamedQubit(f"QB{j + 1}") for j in [qb, 2]]
        circuit = cirq.Circuit()

        circuit.append(cirq.H(q[0]))
        circuit.append(cirq.CNOT(q[0], q[1]))

        circuit.append(cirq.measure(*q, key="M"))

        decomposed_circuit = adonis.decompose_circuit(circuit)

        result = sampler.run(decomposed_circuit, repetitions=shots)
        counts = result.histogram(key='M', fold_func=fold_func)

        values = counts.values()
        values_list = list(values)

        vd = 0  # Variational distance
        fid1 = 0  # Fidelity
        for i in range(len(counts)):
            vd += np.abs(values_list[i] / shots - id_dist[i])
            vd = 0.5 * vd
            fid1 += np.sqrt((values_list[i] / shots) * id_dist[i])

        bell_vd.append(vd)

        if args.verbose:
            print(" ")
            print(circuit)
            print(counts)
            print(" ")

        print("Fidelity = ", round(fid1, 3))
        print(offset_2 + offset_3, end=" ")
        print("Distance from target ([0,1]) = ", round(bell_vd[count], 3))

        count += 1

    id_dist = [0 for i in range(32)]
    id_dist[0] = 0.5
    id_dist[31] = 0.5

    q = [cirq.NamedQubit(f"QB{j + 1}") for j in range(5)]
    circuit = cirq.Circuit()

    circuit.append(cirq.H(q[2]))
    for qb in [0, 1, 3, 4]:
        circuit.append(cirq.CNOT(q[2], q[qb]))

    circuit.append(cirq.measure(*q, key="M"))

    decomposed_circuit = adonis.decompose_circuit(circuit)

    result = sampler.run(decomposed_circuit, repetitions=shots)
    counts = result.histogram(key='M', fold_func=fold_func)

    values = counts.values()
    values_list = list(values)

    vd = 0
    fid2 = 0
    for i in range(len(counts)):
        vd += np.abs(values_list[i] / shots - id_dist[i])
        vd = 0.5 * vd
        fid2 += np.sqrt((values_list[i] / shots) * id_dist[i])

    print(" ")
    print(offset + "================================ ")
    print(offset + "    Preparing a GHZ-5 State")
    print(offset + "================================ ")
    print(" ")

    if args.verbose:
        print(" ")
        print(circuit)
        print(counts)

    print(offset_2 + "GHZ-5 -> Fidelity = ", round(fid2, 3))
    print(offset_2 + "GHZ-5 -> Distance from target ([0,1]) = ", round(vd, 3))

    print(" ")
    print(" ")


if __name__ == "__main__":
    main()
