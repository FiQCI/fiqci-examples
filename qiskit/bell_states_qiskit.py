import argparse
import os
from argparse import RawTextHelpFormatter

from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.fake_backends import IQMFakeAdonis
from qiskit_aer import Aer

from qiskit import QuantumCircuit, QuantumRegister, transpile

"""
Create and measure a bell state. User lists the pairs to entangle.

If the backend is not the simulator then require the qubit pair to be put in.

User allowed to pick any pair or restrict them to only pick pairs with QB3
Compare simulator vs real devices. CNOT gate on different target/control qubits to see the difference.

"""


def print_header(s):
    """
    Prints a section header.
    """
    print("\n" + f"=== {s.upper()} ===")


def get_args():

    args_parser = argparse.ArgumentParser(
        description="""Bell States Example""",
        formatter_class=RawTextHelpFormatter,
        epilog="""Example usage:
        python bell_states_qiskit.py --backend simulator
        python bell_states_qiskit.py --backend simulator --verbose (prints circuits)
        """,
    )

    # Parse Arguments

    args_parser.add_argument(
        "--backend",
        help="""
        Define the backend for running the program.
        'aer'/'simulator' runs on Qiskit's aer simulator,
        'helmi' runs on the Helmi Quantum Computer
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
    print("Running on backend = ", args.backend)

    if args.backend == 'helmi':
        # Set up the Helmi backend
        HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
        if not HELMI_CORTEX_URL:
            print("""Environment variable HELMI_CORTEX_URL is not set.
                  Are you running on Lumi and on the q_fiqci node?.
                  Falling back to fake backend.""")
            # raise ValueError("Environment variable HELMI_CORTEX_URL is not set")

        else:
            provider = IQMProvider(HELMI_CORTEX_URL)
            backend = provider.get_backend()
    else:
        provider = Aer
        backend = provider.get_backend('aer_simulator')

    print_header("Preparing a Bell State: |00> + |11> / sqrt(2)")

    for qb in [0, 1, 3, 4]:

        print_header("Control: QB" + str(qb + 1) + "  Target: QB3 -> ")
        qreg = QuantumRegister(2, "qB")
        qc = QuantumCircuit(qreg)

        qc.h(qreg[0])
        qc.cx(qreg[0], qreg[1])
        qc.measure_all()

        if args.verbose:
            print(qc.draw())

        shots = 1000

        qubit_mapping = {
            qreg[0]: qb,
            qreg[1]: 2,
        }

        qc = transpile(
            qc, backend, optimization_level=0,
            initial_layout=qubit_mapping,
        )

        if args.verbose:
            print(qc.draw())

        job = backend.run(qc, shots=shots)

        counts = job.result().get_counts()

        if args.verbose and "IQM" in str(backend):
            print("Mapping")
            try:
                print(job.result().results[0].metadata['input_qubit_map'])
            except AttributeError:
                print(job.result().request.qubit_mapping)

        t2 = ((counts.get("00", 0) + counts.get("11", 0)) / shots) * 100

        counts_00 = (counts.get("00", 0) / shots) * 100
        counts_11 = (counts.get("11", 0) / shots) * 100

        if "10" in counts:
            counts_10 = (counts["10"] / shots) * 100
        else:
            counts_10 = 0

        if "01" in counts:
            counts_01 = (counts["01"] / shots) * 100
        else:
            counts_01 = 0
        print("Percentage counts |00> = ", round(counts_00, 2), "%")
        print("Percentage counts |11> = ", round(counts_11, 2), "%")
        print("Percentage counts |10> = ", round(counts_10, 2), "%")
        print("Percentage counts |01> = ", round(counts_01, 2), "%")
        print("Percentage of counts |00> or |11> = ", round(t2, 2), "%")

        print_header("Control: QB3" + "  Target QB" + str(qb + 1) + " -> ")
        qreg = QuantumRegister(2, "qB")
        qc = QuantumCircuit(qreg)

        qc.h(qreg[1])
        qc.cx(qreg[1], qreg[0])
        qc.measure_all()

        if args.verbose:
            print(qc.draw())

        shots = 1000

        qubit_mapping = {
            qreg[0]: qb,
            qreg[1]: 2,
        }

        qc = transpile(
            qc, backend, optimization_level=0,
            initial_layout=qubit_mapping,
        )

        if args.verbose:
            print(qc.draw())

        job = backend.run(qc, shots=shots)

        counts = job.result().get_counts()

        if args.verbose and "IQM" in str(backend):
            print("Mapping")
            try:
                print(job.result().results[0].metadata['input_qubit_map'])
            except AttributeError:
                print(job.result().request.qubit_mapping)
        t2 = ((counts.get("00", 0) + counts.get("11", 0)) / shots) * 100

        counts_00 = (counts.get("00", 0) / shots) * 100
        counts_11 = (counts.get("11", 0) / shots) * 100

        if "10" in counts:
            counts_10 = (counts["10"] / shots) * 100
        else:
            counts_10 = 0

        if "01" in counts:
            counts_01 = (counts["01"] / shots) * 100
        else:
            counts_01 = 0
        print("Percentage counts |00> = ", round(counts_00, 2), "%")
        print("Percentage counts |11> = ", round(counts_11, 2), "%")
        print("Percentage counts |10> = ", round(counts_10, 2), "%")
        print("Percentage counts |01> = ", round(counts_01, 2), "%")
        print("Percentage of counts |00> or |11> = ", round(t2, 2), "%")


if __name__ == "__main__":
    main()
