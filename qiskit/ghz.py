import argparse
import os
from argparse import RawTextHelpFormatter

import numpy as np
from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.fake_backends import IQMFakeAdonis
from qiskit import QuantumCircuit, QuantumRegister, transpile
from qiskit_aer import Aer

"""

This example creates a 5 qubit GHZ state in qiskit

First a Bell state is prepared between QB3 and all the other qubits.
From this we can measure the trace distance between QB3 and each of the other qubits.

A 5 qubit GHZ state is then created

In this example we calculate the fidelity and Distance from target state for each bell state
and then the 5 qubit GHZ state

- Fidelity is the "closeness" of two quantum states or how distinguishable they are from each other
    - For example a maximum value of 1 is attained if and only if the two states are identical.
    - There is good discussion found here: http://theory.caltech.edu/~preskill/ph219/chap2_15.pdf

- The "Distance from target" or the Trace Distance is the Quantum generalization of the "statistical distance"
    or Kolmogorov distance
    It is another measure of the distinguishability between two quantum states
"""
def print_header(s):
    """
    Prints a section header.
    """
    print("\n" + f"=== {s.upper()} ===")

def get_args():

    args_parser = argparse.ArgumentParser(
        description="""
        This example creates a 5 qubit GHZ stats in cirq
        First a Bell state is prepared between QB3 and all the other qubits.
        From this we can measure the trace distance between QB3 and each of the other qubits.""",
        formatter_class=RawTextHelpFormatter,
        epilog="""Example usage:
        python ghz.py --backend simulator
        python ghz.py --backend simulator --verbose (prints circuits)
        """,
    )
    # Parse Arguments

    args_parser.add_argument(
        "--backend",
        help="""
        Define the backend for running the program.
        'aer'/'simulator' runs on Qiskit's aer simulator,
        'helmi' runs on VTT Helmi Quantum Computer
        """,
        required=True,
        type=str,
        choices=["helmi", "simulator"],
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


def main():
    args = get_args()
    backend = IQMFakeAdonis()
    if args.backend == 'helmi':
        # Set up the Helmi backend
        HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
        if not HELMI_CORTEX_URL:
            print('Environment variable HELMI_CORTEX_URL is not set. Are you running on Lumi and on the q_fiqci node?. Falling back to fake backend.')
            #raise ValueError("Environment variable HELMI_CORTEX_URL is not set")

        else:
            provider = IQMProvider(HELMI_CORTEX_URL)
            backend = provider.get_backend()
    else:
        provider = Aer
        backend = provider.get_backend('aer_simulator')


    shots = 10000

    bell_vd = []
    id_dist = [0.5, 0, 0, 0.5]
    
    print_header("Preparing a Bell State")
    count = 0
    for qb in [0, 1, 3, 4]:
        print("QB" + str(qb + 1) + " and QB3 -> ", end=" ")
        qreg = QuantumRegister(2, "qB")
        circuit = QuantumCircuit(qreg)

        circuit.h(qreg[0])
        circuit.cx(qreg[0], qreg[1])

        circuit.measure_all()

        if args.verbose:
            print(" ")
            print(circuit.draw())

        mapping = {
            qreg[0]: qb,  # map first virtual qubit to qubit in list
            qreg[1]: 2,
        }   # map second virtual qubit to QB3

        # Run job on the circuit
        circuit = transpile(circuit, backend, optimization_level=0, initial_layout=mapping)
        job = backend.run(circuit, shots=shots)
        counts = job.result().get_counts()

        if args.verbose:
            print(f"Counts: {counts}")
            if "IQM" in str(backend):
                try:
                    print(job.result().results[0].metadata['input_qubit_map'])
                except AttributeError:
                    print(job.result().request.qubit_mapping)

        values = counts.values()
        values_list = list(values)

        vd = 0
        fid1 = 0
        for i in range(len(counts)):
            vd += np.abs(values_list[i] / shots - id_dist[i])
            vd = 0.5 * vd
            fid1 += np.sqrt((values_list[i] / shots) * id_dist[i])

        bell_vd.append(vd)

        print("Fidelity = ", round(fid1, 3))
        print("Distance from target ([0,1]) = ", round(bell_vd[count], 3))

        count += 1

    print_header("Preparing a GHZ-5 State")

    id_dist = [0 for i in range(32)]
    id_dist[0] = 0.5
    id_dist[31] = 0.5

    qreg = QuantumRegister(5, "qB")
    circuit = QuantumCircuit(qreg)

    circuit.h(qreg[2])
    for qb in [0, 1, 3, 4]:
        circuit.cx(qreg[2], qreg[qb])

    circuit.measure_all()

    if args.verbose:
        print(" ")
        print(circuit.draw())

    circuit = transpile(circuit, backend, layout_method="sabre", optimization_level=3)
    job = backend.run(circuit, shots=shots)
    counts = job.result().get_counts()

    if args.verbose:
        print(f"Counts: {counts}")
        if "IQM" in str(backend):
            try:
                print(job.result().results[0].metadata['input_qubit_map'])
            except AttributeError:
                print(job.result().request.qubit_mapping)

    values = counts.values()
    values_list = list(values)

    vd = 0
    fid2 = 0
    for i in range(len(counts)):
        vd += np.abs(values_list[i] / shots - id_dist[i])
        vd = 0.5 * vd
        fid2 += np.sqrt((values_list[i] / shots) * id_dist[i])

    print("GHZ-5 -> Fidelity = ", round(fid2, 3))
    print("GHZ-5 -> Distance from target ([0,1]) = ", round(vd, 3))

    print(" ")
    print(" ")


if __name__ == "__main__":
    main()
