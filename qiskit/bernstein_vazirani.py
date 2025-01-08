import argparse
import os
from argparse import RawTextHelpFormatter
from collections import Counter
from random import randint

from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.fake_backends import IQMFakeAdonis
from qiskit_aer import Aer

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile

"""

This example shows the Bernstein-Vazirani Algorithm.
Bernstein-Vazirani Algorithm is an extension of the Deutsch-Joza algorithm. The algorithm tries to search
for a bit string from a hidden function.

The Solution:

- Intialize the qubits to |0> state and an output qubit to |->
- Apply Hadamard gates to the input qubits
- Call the BV Oracle
- Apply Hadamard gates to the input qubits
- Measure

This is a 5 qubit circuit with the last qubit used as an "output qubit". Hence only needing a classical register
of size 4 despite having a quantum register of size 5.

"""


class BVoracle:
    """
    Class to define the Bernstein-Vazirani Oracle.
    """

    def __init__(self, backend, dim=4, num=None, verbose=False):
        self._num = num if num else randint(0, 2**dim - 1)
        self.dim = dim
        self.backend = backend
        self.ccalls = 0
        self.qcalls = 0
        self.verbose = verbose

    def get(self, x):
        assert len(x) == self.dim
        # ccalls increases every time one queries the oracle
        self.ccalls += 1
        s = self._to_bin_digits(self._num)
        return sum(x[i] * s[i] for i in range(self.dim)) % 2

    # Assuming that when one calls the qoracle to be created
    # dim is correctly stated
    def quantum(self, shots=1):
        # qcalls increases every time one queries the oracle
        self.qcalls += 1
        qreg = QuantumRegister(5, "QB")
        creg = ClassicalRegister(4, "c")
        qc = QuantumCircuit(qreg, creg)
        qc = self._prepare_circuit(qc, qreg)

        job = self.backend.run(qc, shots=shots)

        return job.result().get_counts()

    def _prepare_circuit(self, qc, qreg):
        # Prepare the additional qubit
        qc.h(qreg[4])
        qc.z(qreg[4])
        for i in range(4):
            qc.h(i)

        s = self._to_bin_digits(self._num)[::-1]
        print(self._num, s)
        for q in range(4):
            if s[q] != 0:
                qc.cx(q, qreg[4])

        for i in range(4):
            qc.h(i)

        qc.measure(range(4), range(4))
        transpiled_circuit = transpile(
            qc, self.backend, layout_method='sabre', optimization_level=3,
        )
        if self.verbose:
            print("Created circuit: ")
            print(qc.draw())
            print("Transpiled circuit: ")
            print(transpiled_circuit.draw())

        return transpiled_circuit

    def _to_bin_digits(self, num, dim=4):
        """
        Returns binary representation of num (int) as a list of ints with optional
        parameter dim to fill with zeroes from left up to length dim.
        """
        return [int(c) for c in self._to_bin_str(num, dim)]

    def _to_bin_str(self, num, dim=4):
        """
        Returns binary representation of num (int) as a string with optional
        parameter dim to fill with zeroes from left up to length dim.
        """
        return f"{num:0{dim}b}"


def get_args():
    """
    Parse arguments.
    """
    args_parser = argparse.ArgumentParser(
        description="""
        This example creates a 5 qubit GHZ stats in qiskit
        First a Bell state is prepared between QB3 and all the other qubits.
        From this we can measure the trace distance between QB3 and each of the other qubits.""",
        formatter_class=RawTextHelpFormatter,
        epilog="""Example usage:
        python bernstein_vazirani.py --backend helmi
        python bernstein_vazirani.py --backend simulator
        python bernstein_vazirani.py --backend helmi -v (prints circuits)
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

    args_parser.add_argument(
        "-o",
        "--option",
        help="""
        1 - Single Quantum run
        2 - Repeated Quantum run
            MUST specify how many repeats with --repeats option.
        """,
        required=False,
        type=int,
        default=2,
    )

    args_parser.add_argument(
        "--number",
        help="""
        Choose the random bit string number in decimal form
        E.g --number 7.
        """,
        required=False,
        type=int,
        default=None,
    )

    args_parser.add_argument(
        "--repeats",
        help="""
        Number of repeats of the repeated Quantum Run
        This option can be specified without using the --option
        Default = 5
        """,
        type=int,
        required=False,
        default=5,
    )

    return args_parser.parse_args()


# def classical(bv):
#     """Execution of classical algorithm"""
#     b = ""
#     for num in range(bv.dim):
#         x = bin_digits(2**num, bv.dim)
#         b += str(bv.get(x))
#     return b[::-1]

def print_header(s):
    """
    Prints a section header.
    """
    print("\n" + f"=== {s.upper()} ===")


def most_frequent(lst):
    """
    Returns the most frequent item in a list.
    """
    freqs = Counter(lst)
    most_freq_item = max(freqs, key=freqs.get)
    return most_freq_item, freqs[most_freq_item]


def secret_count(lst, secret):
    """
    Returns the number of times the secret number appears in the list.
    """
    return lst.get(f"{secret:0{4}b}", 0)


def main():
    args = get_args()
    backend = IQMFakeAdonis()
    if args.backend == 'helmi':
        # Set up the Helmi backend
        HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
        if not HELMI_CORTEX_URL:
            print('Environment variable HELMI_CORTEX_URL is not set. Are you running on Lumi and on the q_fiqci node?. Falling back to fake backend.')
            # raise ValueError("Environment variable HELMI_CORTEX_URL is not set")

        else:
            provider = IQMProvider(HELMI_CORTEX_URL)
            backend = provider.get_backend()
    else:
        provider = Aer
        backend = provider.get_backend('aer_simulator')

    if args.number is not None and args.number > 15:
        raise ValueError(
            "ERROR! Guess must be a 4 bit string number or lower. Less than or equal to 15.",
        )

    print("Running on backend = ", args.backend)

    print_header("initialization")
    NUM = args.number
    if NUM is None:
        NUM = randint(0, 15)
        print("The hidden oracle number was chosen randomly and will not be disclosed.")
    else:
        print(f"""The hidden oracle number is s = {
            NUM
        }. In general it is not dislosed to the testing party.""")

    bv = BVoracle(num=NUM, backend=backend, verbose=args.verbose)
    print("The oracle is now initialized with given secret oracle index.")

    if args.option == 1:
        guess = bv.quantum(shots=10000)
        s, amt = most_frequent(guess)
        if bv._num != int(s, 2):
            success_rate = secret_count(guess, bv._num)
        else:
            success_rate = round((amt / 1000) * 100, 2)
        print(s, amt)

        print_header("Single run")
        print(f"Success Chance: {success_rate}%")
        print(f"Result: {int(s, 2)}")
        print(f"Binary: {s}")
        print(f"Secret number: {bv._num}")

        print(f"""Guessed outcome is s = {int(s, 2)} (binary number {s}) found in {
            amt
        } shots out of 1 repeats.""")
        print(f"Quantum oracle was called {bv.qcalls} time(s).")
        print("\n")

    elif args.option == 2:
        success = []
        result = []
        binary = []
        qcalls = []
        print_header("Repeated run")
        for i in range(args.repeats):
            guess = bv.quantum(shots=1000)
            s, amt = most_frequent(guess)
            if bv._num != int(s, 2):
                success_rate = secret_count(guess, bv._num)
            else:
                success_rate = round((amt / 1000) * 100, 2)
            success.append(success_rate)
            result.append(int(s, 2))
            binary.append(s)
            qcalls.append(bv.qcalls)

        print("Run  Success      Result     Binary     Secret     qcalls")
        for i in range(args.repeats):
            print(
                str(i + 1)
                + "     "
                + str(success[i])
                + "%         "
                + str(result[i])
                + "         "
                + str(binary[i])
                + "         "
                + str(bv._num)
                + "         "
                + str(qcalls[i])
                + "",
            )


if __name__ == "__main__":
    main()
