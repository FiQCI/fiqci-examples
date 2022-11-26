import sys
import argparse
from argparse import RawTextHelpFormatter

import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.compiler import transpile
import numpy as np

from csc_qu_tools.qiskit import Helmi as helmi

"""
Create and measure a bell state. User lists the pairs to entangle.

If the backend is not the simulator then require the qubit pair to be put in.

User allowed to pick any pair or restrict them to only pick pairs with QB3
Compare simulator vs real devices. CNOT gate on different target/control qubits to see the difference.

"""


def get_args():

    args_parser = argparse.ArgumentParser(
        description="""Bell States Example""",
        formatter_class=RawTextHelpFormatter,
        epilog="""Example usage:
        python bell_states_qiskit.py --backend simulator
        python bell_states_qiskit.py --backend simulator --noise
        python bell_states_qiskit.py --backend simulator --verbose (prints circuits)
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

    print(" ")
    print("   Preparing a Bell State")
    print("   |00> + |11> / sqrt(2)")
    print(" ")
    id_dist = [0.5, 0, 0, 0.5]

    offset = " " * 10
    offset2 = " " * 20

    for qb in [0, 1, 3, 4]:

        print(offset + "Control: QB" + str(qb + 1) + "  Target: QB3 -> ")
        qreg = QuantumRegister(2, "qB")
        creg = ClassicalRegister(2, "c")
        qc = QuantumCircuit(qreg, creg)

        qc.h(qreg[0])
        qc.cx(qreg[0], qreg[1])
        qc.measure(range(2), range(2))

        if args.verbose == True:
            print(qc.draw())

        qc_decomposed = transpile(qc, basis_gates=basis_gates)

        shots = 10000

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

        t2 = ((counts["00"] + counts["11"]) / shots) * 100

        counts_00 = (counts["00"] / shots) * 100
        counts_11 = (counts["11"] / shots) * 100

        if "10" in counts:
            counts_10 = (counts["10"] / shots) * 100
        else:
            counts_10 = 0

        if "01" in counts:
            counts_01 = (counts["01"] / shots) * 100
        else:
            counts_01 = 0
        print(offset2 + " Percentage counts |00> = ", round(counts_00, 2), "%")
        print(offset2 + " Percentage counts |11> = ", round(counts_11, 2), "%")
        print(offset2 + " Percentage counts |10> = ", round(counts_10, 2), "%")
        print(offset2 + " Percentage counts |01> = ", round(counts_01, 2), "%")
        print(offset2 + " Percentage of counts |00> or |11> = ", round(t2, 2), "%")

        print(offset + "Control: QB3" + "  Target QB" + str(qb + 1) + " -> ")
        qreg = QuantumRegister(2, "qB")
        creg = ClassicalRegister(2, "c")
        qc = QuantumCircuit(qreg, creg)

        qc.h(qreg[1])
        qc.cx(qreg[1], qreg[0])
        qc.measure(range(2), range(2))

        if args.verbose == True:
            print(qc.draw())

        qc_decomposed = transpile(qc, basis_gates=basis_gates)

        shots = 1000

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

        t2 = ((counts["00"] + counts["11"]) / shots) * 100

        counts_00 = (counts["00"] / shots) * 100
        counts_11 = (counts["11"] / shots) * 100

        if "10" in counts:
            counts_10 = (counts["10"] / shots) * 100
        else:
            counts_10 = 0

        if "01" in counts:
            counts_01 = (counts["01"] / shots) * 100
        else:
            counts_01 = 0
        print(offset2 + " Percentage counts |00> = ", round(counts_00, 2), "%")
        print(offset2 + " Percentage counts |11> = ", round(counts_11, 2), "%")
        print(offset2 + " Percentage counts |10> = ", round(counts_10, 2), "%")
        print(offset2 + " Percentage counts |01> = ", round(counts_01, 2), "%")
        print(offset2 + " Percentage of counts |00> or |11> = ", round(t2, 2), "%")


if __name__ == "__main__":
    main()
