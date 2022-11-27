# Single qubit flipping

import sys
import argparse
from argparse import RawTextHelpFormatter

import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.compiler import transpile

from csc_qu_tools.qiskit import Helmi as helmi


def get_args():

    args_parser = argparse.ArgumentParser(
        description="""
        Single qubit flipping.
        This example gives different options for flipping different qubits in Helmi""",
        formatter_class=RawTextHelpFormatter,
        epilog="""Example usage:
        python qb_flip_qiskit.py --backend helmi --verbose
        (default) python qb_flip_qiskit.py --backend aer
        (default) python qb_flip_qiskit.py --backend aer --option 3
        python qb_flip_qiskit.py --backend simulator --qubit 3
        python qb_flip_qiskit.py --backend helmi --option 1
        """,
    )

    # Parse Arguments

    args_parser.add_argument(
        "--backend",
        help="""
        Define the backend for running the program.
        'aer' runs on Qiskit's aer simulator, 
        'helmi' runs on VTT Helmi Quantum Computer
        """,
        required=False,
        type=str,
        default=None,
        choices=["helmi", "aer", "simulator"],
    )

    args_parser.add_argument(
        "-o",
        "--option",
        help="""
        1 - flip one at a time
        2 - flip all at once
        3 - Both of the above
        4 - Choose a specific qubit to flip. 
            MUST specify a qubit with --qubit option.
        """,
        required=False,
        type=int,
        default=3,
    )

    args_parser.add_argument(
        "--qubit",
        help="""
        An integer representing the qubit in the physical register
        Indexing starts at 0. Enter 0,1,2,3,4.
        This option can be specified without using the --option
        """,
        type=int,
        required=False,
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

    if (
        args_parser.parse_args().qubit in [0, 1, 2, 3, 4]
        and args_parser.parse_args().option != 4
    ):
        print(args_parser.parse_args().option)
        sys.argv.extend(["--option", "4"])
        print(args_parser.parse_args().option)

    if (
        (
            args_parser.parse_args().backend == None
            or args_parser.parse_args().option == None
        )
        or args_parser.parse_args().option not in [1, 2, 3, 4]
        or (
            args_parser.parse_args().option == 4
            and args_parser.parse_args().qubit == None
        )
        or args_parser.parse_args().qubit not in [0, 1, 2, 3, 4, None]
        or (
            args_parser.parse_args().noise == True
            and args_parser.parse_args().backend == "helmi"
        )
    ):
        args_parser.print_help()
        exit()

    return args_parser.parse_args()


def flip_qubits(backend_dict, qubit, option: int):

    shots = 10000
    init_state = 0

    backend = backend_dict["backend"]
    basis_gates = backend_dict["basis_gates"]

    if option == 1:
        print("      QB" + str(qubit + 1) + " -> ", end=" ")
        qreg = QuantumRegister(1, "qb")
        creg = ClassicalRegister(1, "c")
        qc = QuantumCircuit(qreg, creg)
        # qc.initialize(init_state, 0) # Intialize to |1>
        qc.x(0)
        qc.measure(range(1), range(1))

    elif option == 2:
        qreg = QuantumRegister(5, "qb")
        creg = ClassicalRegister(5, "c")
        qc = QuantumCircuit(qreg, creg)
        for j in range(5):
            # qc.initialize(init_state, j) # Intialize to |1>
            qc.x(j)
        qc.measure(range(5), range(5))
    else:
        sys.exit("Option 1 or 2 only")

    # #Draw the circuit
    if verbose == True:
        print(" ")
        print(qc.draw())

    # #Transpile into native gates
    qc_decomposed = transpile(qc, basis_gates=basis_gates)

    # Map virtual and physical qubits (routing)
    if "IQMBackend" or "fake_helmi" in str(backend):
        virtual_qubits = qc_decomposed.qubits
        if option == 1:
            qubit_mapping = {virtual_qubits[0]: "QB" + str(qubit + 1)}
        elif option == 2:
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

    # #Run job on the QC
    job = backend.run(qc_decomposed, shots=shots, qubit_mapping=qubit_mapping)

    counts = job.result().get_counts()
    print(counts)
    if str(init_state) not in counts:
        counts[str(init_state)] = 0

    if option == 1:
        success_rate = ((shots - counts[str(init_state)]) / shots) * 100
        print(" Success rate ", round(success_rate, 3), " %")
    elif option == 2:
        l = [str(init_state) * 5]
        s = "".join("1" if x == "0" else "0" for x in str(l[0]))
        success_rate = (counts[str(s)] / shots) * 100
        print("      Success rate ", round(success_rate, 3), " %")
    else:
        sys.exit("Option 1 or 2 only")


def main():

    args = get_args()

    global verbose
    verbose = args.verbose

    print("Running on backend = ", args.backend)

    if args.backend == "simulator" or args.backend == "aer":
        from qiskit.providers.aer import AerSimulator

        if args.noise == True:
            from csc_qu_tools.qiskit.mock import FakeHelmi

            print(
                "Inducing artificial noise into Simulator with FakeHelmi Noise Model"
            )
            basis_gates = ["r", "cz"]
            backend = FakeHelmi()
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

    if args.option == 1:
        print(" ")
        print("   Flip one qubit at a time")
        print(" ")
        for qb in range(5):
            flip_qubits(backend_dict, qb, 1)

    elif args.option == 2:
        print(" ")
        print("   Flip all qubits at once")
        print(" ")
        flip_qubits(backend_dict, None, 2)

    elif args.option == 3:
        print(" ")
        print("   Flip one qubit at a time")
        print(" ")
        for qb in range(5):
            flip_qubits(backend_dict, qb, 1)
        print(" ")
        print("   Flip all qubits at once")
        print(" ")
        flip_qubits(backend_dict, None, 2)

    elif args.option == 4:
        qb = int(args.qubit)
        print(" ")
        print("   Flipping QB" + str(qb + 1))
        print(" ")
        flip_qubits(backend_dict, qb, 1)
    else:
        sys.exit("Error in argument options")


if __name__ == "__main__":
    main()
