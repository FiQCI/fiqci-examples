import sys
import argparse
from argparse import RawTextHelpFormatter

import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import AncillaRegister
from qiskit.compiler import transpile
import numpy as np

from random import randint

from csc_qu_tools.qiskit import Helmi as helmi

"""

This example shows the Bernstein-Vazirani Algorithm. 


We are trying to find an encoded string



"""
offset=' '*37
offset_2=' '*10
offset_3=' '*50

def get_args():

    args_parser = argparse.ArgumentParser(
        description='''
        This example creates a 5 qubit GHZ stats in cirq
        First a Bell state is prepared between QB3 and all the other qubits.
        From this we can measure the trace distance between QB3 and each of the other qubits.''',
        formatter_class=RawTextHelpFormatter,
        epilog='''Example usage:
        python ghz.py --backend simulator
        python ghz.py --backend simulator --noise
        python ghz.py --backend simulator --verbose (prints circuits)
        '''
         )
    # Parse Arguments

    args_parser.add_argument(
        '--backend',
        help='''
        Define the backend for running the program.
        'aer'/'simulator' runs on Qiskit's aer simulator, 
        'helmi' runs on VTT Helmi Quantum Computer
        ''',
        required=False,
        type=str,
        default=None,
        choices=['helmi', 'aer', 'simulator']

    )

    args_parser.add_argument(
        '--verbose', '-v',
        help='''
        Increase the output verbosity
        ''',
        required=False,
        action="store_true"
    )

    args_parser.add_argument(
        '--noise', '-n',
        help='''
        Add noise to the simulation.
        Only use with simulator backend.
        ''',
        required=False,
        action="store_true"
    )


    args_parser.add_argument(
        '-o', '--option',
        help='''
        1 - Single Quantum run
        2 - Repeated Quantum run
            MUST specify how many repeats with --repeats option.
        ''',
        required=False,
        type=int,
        default=2
    )

    args_parser.add_argument(
        '--repeats',
        help='''
        Number of repeats of the repeated Quantum Run
        This option can be specified without using the --option
        Default = 5
        ''',
        type=int,
        required=False,
        default=5

    )

    if (args_parser.parse_args().backend==None) or \
    (args_parser.parse_args().noise==True and args_parser.parse_args().backend=="helmi"):
        args_parser.print_help()
        exit()

 
    return args_parser.parse_args()

def bin_str(num, dim=4):
    """
    Returns binary representation of num (int) as a string with optional
    parameter dim to fill with zeroes from left up to length dim.
    """
    return f"{num:0{dim}b}"

def bin_digits(num, dim=4):
    """
    Returns binary representation of num (int) as a list of ints with optional
    parameter dim to fill with zeroes from left up to length dim.
    """
    return [int(c) for c in bin_str(num, dim)]

class BVoracle:

    def __init__(self, dim=4, num=None, backend_dict=None):
        if num == None:
            num = randint(0, 2 ** dim - 1)
        self._num = num
        self.dim = dim
        self.backend_dict = backend_dict
        self.ccalls = 0
        self.qcalls = 0
        if backend_dict == None:
            print('Call BVOracle with backend_dict')
            exit(0)

    def get(self, x):
        assert len(x) == self.dim
        ## ccalls increases every time one queries the oracle
        self.ccalls += 1
        res = 0
        s = bin_digits(self._num, self.dim)
        for i in range(self.dim):
            res += x[i] * s[i]
        return res % 2

    ## Assuming that when one calls the qoracle to be created
    ## dim is correctly stated
    def quantum(self, shots=1, qubit_mapping=None):
        backend = self.backend_dict['backend']
        basis_gates= self.backend_dict['basis_gates']


        ## qcalls increases every time one queries the oracle
        self.qcalls += 1
        qreg = QuantumRegister(5, 'qB')
        creg = ClassicalRegister(4, 'c')
        OUTER_QUBITS = [0,1,3,4]
        qc = QuantumCircuit(qreg, creg)

        ## Prepare the additional qubit
        qc.h(qreg[4])
        qc.z(qreg[4])

        for i in range(4):
            qc.h(i)


        s = bin_digits(self._num)
        s = s[::-1]

        for q in range(4):
            if s[q] == 0:
                continue
            else:
                qc.cx(q, qreg[4])
        
        for i in range(4):
            qc.h(i)

        
        qc.barrier()

        qc.measure(range(4), range(4))


        # qc.measure(5,5)

        qc = helmi.routing(qc)


        if verbose == True:
            print(qc.draw())


        qc_decomposed = transpile(qc, basis_gates=basis_gates)
        if verbose == True:
            print(qc_decomposed.draw())

        #Map virtual and physical qubits (routing)
        if ("IQMBackend" in str(backend)):
            virtual_qubits = qc_decomposed.qubits
            qubit_mapping = {virtual_qubits[0]: 'QB1', 
                            virtual_qubits[1]: 'QB2',
                            virtual_qubits[2]: 'QB3',
                            virtual_qubits[3]: 'QB4',
                            virtual_qubits[4]: 'QB5'}


        elif (str(backend)=='aer_simulator'):
            virtual_qubits = qc_decomposed.qubits
            qubit_mapping=None


        job = backend.run(qc_decomposed, shots=shots, qubit_mapping=qubit_mapping)

        return job.result().get_counts()

    def creset(self):
        """
        resets the count of ccalls
        """
        self.ccalls = 0

    def qreset(self):
        """
        resets the count of qcalls
        """
        self.qcalls = 0

def classical(bv):
    """Execution of classical algorithm"""
    b = ""
    for num in range(bv.dim):
        x = bin_digits(2 ** num, bv.dim)
        b += str(bv.get(x))
    return b[::-1]

def print_header(s):
    l = 41
    print(' ')
    print(offset+"".join("=" for _ in range(l + 8)))
    print(offset_3+f"=== {s.upper()} ===")
    print(offset+"".join("=" for _ in range(l + 8)))
    print(' ')

def most_frequent(lst):
    most_freq_item = max(lst, key=lst.get)
    # print("Maximum value:",most_freq_item)

    return most_freq_item, lst[most_freq_item]


def main():

    NUM = None

    args=get_args()

    global verbose

    verbose = args.verbose

    print('Running on backend = ', args.backend)

    if args.backend == 'simulator' or args.backend == 'aer':
        from qiskit.providers.aer import AerSimulator

        if args.noise == True:
            import qiskit.providers.aer.noise as noise
            print("Inducing artificial noise into Simulator with a DepolarizingChannel p=0.01")
            error = noise.depolarizing_error(0.01, 1)
            noise_model = noise.NoiseModel()
            noise_model.add_all_qubit_quantum_error(error, ['r'])
            basis_gates=['r', 'cz']
            backend = AerSimulator(noise_model=noise_model)
        else:
            basis_gates=['r', 'cz']
            backend = AerSimulator()

    elif (args.backend == 'helmi'):
        provider = helmi()
        backend = provider.set_backend()
        basis_gates = provider.basis_gates

    else:
        sys.exit("Backend option not recognised")

    
    backend_dict = dict([('backend', backend), ('basis_gates', basis_gates)])

    print_header("initialization")
    if NUM is None:
        NUM = randint(0, 15)
        print(offset+f"The hidden oracle number was chosen randomly and will not be disclosed.")
    else:
        print(offset+f"The hidden oracle number is s = {NUM}. In general it is not dislosed to the testing party.")

    bv = BVoracle(num=NUM, backend_dict=backend_dict)
    print(offset+"The oracle is now initialized with given secret oracle index.")


    if args.option == 1:

        guess = bv.quantum(shots=10000)
        # print(guess)

        # results=list(guess.data[0:5].T.to_numpy()[0])
        s, amt = most_frequent(guess)
        success_rate = round((amt/1000)*100,2)
        print(s, amt)

        print_header('Single run')
        print(offset+"Success Chance:  "+str(success_rate)+'%')
        print(offset+"Result:  "+str(int(s,2)))
        print(offset+"Binary:  "+str(s))

        print(offset+f"Guessed outcome is s = {int(s,2)} (binary number {s}) found in {amt} shots out of 1 repeats.")
        print(offset+f"Quantum oracle was called {bv.qcalls} time(s).")
        print("\n")

    elif args.option == 2:
        success = []
        result = []
        binary = []
        qcalls = []
        print_header('Repeated run')
        for i in range(args.repeats):
            guess = bv.quantum(shots=1000)
            s, amt = most_frequent(guess)
            success_rate = round((amt/1000)*100,2)
            success.append(success_rate)
            result.append(int(s,2))
            binary.append(s)
            qcalls.append(bv.qcalls)

        print(offset+'Run  Success      Result     Binary     qcalls')
        for i in range(args.repeats):
            print(offset+str(i+1)+'     '+str(success[i])+'%         '+str(result[i])+'         '+str(binary[i])+'         '+str(qcalls[i])+'')






    '''

    To-do:

    The above.
    Add verbosity.
    Add options:
        - Choosing own number or string. -s --secret
        - Choosing single run or multiple repeated runs
        - Choose to do classical
    '''
    




if __name__ == '__main__':
    main()