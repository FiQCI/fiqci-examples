import sys
import argparse
from argparse import RawTextHelpFormatter

import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.compiler import transpile
import numpy as np

from csc_qu_tools.qiskit import Helmi as helmi

"""

This example creates a 5 qubit GHZ stats in cirq

First a Bell state is prepared between QB3 and all the other qubits.
From this we can measure the trace distance between QB3 and each of the other qubits.

A 5 qubit GHZ state is then created 

In this example we calculate the fidelity and Distance from target state for each bell state adn then the 5 qubit GHZ state

- Fidelity is the "closeness" of two quantum states or how distinguishable they are from each other 
    - For example a maximum value of 1 is attained if and only if the two states are identical. 
    - There is good discussion found here: http://theory.caltech.edu/~preskill/ph219/chap2_15.pdf

- The "Distance from target" or the Trace Distance is the Quantum generalization of the "statistical distance"
    or Kolmogorov distance
    It is another measure of the distinguishability between two quantum states
"""


def get_args():

    args_parser = argparse.ArgumentParser(
        description="""
        This example creates a 5 qubit GHZ stats in cirq
        First a Bell state is prepared between QB3 and all the other qubits.
        From this we can measure the trace distance between QB3 and each of the other qubits.""",
        formatter_class=RawTextHelpFormatter,
        epilog="""Example usage:
        python ghz.py --backend simulator
        python ghz.py --backend simulator --noise
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
        required=False,
        type=str,
        default=None,
        choices=["helmi", "aer", "simulator"],
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

    args_parser.add_argument(
        "--noise",
        "-n",
        help="""
        Add noise to the simulation.
        Only use with simulator backend.
        """,
        required=False,
        action="store_true",
    )

    if (args_parser.parse_args().backend == None) or (
        args_parser.parse_args().noise == True
        and args_parser.parse_args().backend == "helmi"
    ):
        args_parser.print_help()
        exit()

    return args_parser.parse_args()


def main():
    offset = " " * 37
    offset_2 = " " * 10
    offset_3 = " " * 15

    args = get_args()

    print("Running on backend = ", args.backend)

    if args.backend == "simulator" or args.backend == "aer":
        from qiskit.providers.aer import AerSimulator

        if args.noise == True:
            import qiskit.providers.aer.noise as noise

            print(
                "Inducing artificial noise into Simulator with a DepolarizingChannel p=0.01"
            )
            error = noise.depolarizing_error(0.01, 1)
            noise_model = noise.NoiseModel()
            noise_model.add_all_qubit_quantum_error(error, ["r"])
            basis_gates = ["r", "cz"]
            backend = AerSimulator(noise_model=noise_model)
        else:
            basis_gates = ["r", "cz"]
            backend = AerSimulator()

    elif args.backend == "helmi":
        provider = helmi()
        backend = provider.set_backend()
        basis_gates = provider.basis_gates

    else:
        sys.exit("Backend option not recognised")

    backend_dict = dict([("backend", backend), ("basis_gates", basis_gates)])

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
        qreg = QuantumRegister(2, "qB")
        creg = ClassicalRegister(2, "c")
        qc = QuantumCircuit(qreg, creg)

        qc.h(qreg[0])
        qc.cx(qreg[0], qreg[1])

        qc.measure(range(2), range(2))

        if args.verbose == True:
            print(" ")
            print(qc.draw())

        qc_decomposed = transpile(qc, basis_gates=basis_gates)

        # Map virtual and physical qubits (routing)
        if "IQMBackend" in str(backend):
            virtual_qubits = qc_decomposed.qubits
            qubit_mapping = {
                virtual_qubits[0]: "QB" + str(qb + 1),
                virtual_qubits[1]: "QB3",
            }

        elif str(backend) == "aer_simulator":
            virtual_qubits = qc_decomposed.qubits
            qubit_mapping = None

        # #Run job on the QC
        job = backend.run(qc_decomposed, shots=shots, qubit_mapping=qubit_mapping)
        counts = job.result().get_counts()

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
        print(offset_2 + offset_3, end=" ")
        print("Distance from target ([0,1]) = ", round(bell_vd[count], 3))

        count += 1

    print(" ")
    print(offset + "================================ ")
    print(offset + "    Preparing a GHZ-5 State")
    print(offset + "================================ ")
    print(" ")

    id_dist = [0 for i in range(32)]
    id_dist[0] = 0.5
    id_dist[31] = 0.5

    qreg = QuantumRegister(5, "qB")
    creg = ClassicalRegister(5, "c")
    qc = QuantumCircuit(qreg, creg)

    qc.h(qreg[2])
    for qb in [0, 1, 3, 4]:
        qc.cx(qreg[2], qreg[qb])

    qc.measure(range(5), range(5))

    qc_decomposed = transpile(qc, basis_gates=basis_gates)

    # Map virtual and physical qubits (routing)
    if "IQMBackend" in str(backend):
        virtual_qubits = qc_decomposed.qubits
        qubit_mapping = {
            virtual_qubits[0]: "QB1",
            virtual_qubits[1]: "QB2",
            virtual_qubits[2]: "QB3",
            virtual_qubits[3]: "QB4",
            virtual_qubits[4]: "QB5",
        }

    elif str(backend) == "aer_simulator":
        virtual_qubits = qc_decomposed.qubits
        qubit_mapping = None

    if args.verbose == True:
        print(" ")
        print(qc.draw())

    job = backend.run(qc_decomposed, shots=shots, qubit_mapping=qubit_mapping)
    counts = job.result().get_counts()

    values = counts.values()
    values_list = list(values)

    vd = 0
    fid2 = 0
    for i in range(len(counts)):
        vd += np.abs(values_list[i] / shots - id_dist[i])
        vd = 0.5 * vd
        fid2 += np.sqrt((values_list[i] / shots) * id_dist[i])

    print(offset_2 + "GHZ-5 -> Fidelity = ", round(fid2, 3))
    print(offset_2 + "GHZ-5 -> Distance from target ([0,1]) = ", round(vd, 3))

    print(" ")
    print(" ")


if __name__ == "__main__":
    main()
