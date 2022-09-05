# Single qubit flipping

import sys
import argparse
from argparse import RawTextHelpFormatter
import math

from csc_qu_tools.cirq import Helmi
import cirq


def get_args():

    args_parser = argparse.ArgumentParser(description='Single qubit flipping.', formatter_class=RawTextHelpFormatter)

    # Parse Arguments

    args_parser.add_argument(
        '--backend',
        help='''
        Define the backend for running the program.
        'simulator' runs on Cirq's Simulator, 
        'helmi' runs on VTT Helmi Quantum Computer
        ''',
        required=True,
        type=str,
        default=None

    )

    args_parser.add_argument(
        '-o', '--option',
        help='''
        1 - flip one at a time
        2 - flip all at once
        3 - Both of the above
        4 - Choose a specific qubit to flip. 
            MUST specify a qubit with --qubit option.
        ''',
        required=False,
        type=int,
        default=3
    )


    args_parser.add_argument(
        '--qubit',
        help='''
        An integer representing the qubit in the physical register
        Indexing starts at 0. Enter 0,1,2,3,4.
        ''',
        type=int,
        required=False,
        default=None

    )



    if (args_parser.parse_args().backend==None or \
        args_parser.parse_args().option==None) or \
        args_parser.parse_args().option not in [1,2,3,4] or \
        (args_parser.parse_args().option == 4 and args_parser.parse_args().qubit == None) or \
        args_parser.parse_args().qubit not in [0,1,2,3, 4, None]:
        args_parser.print_help()
        exit()

 
    return args_parser.parse_args()


def flip_qubits(backend, qubit, option: int):
    shots=1024

    c = cirq.Circuit()

    if option == 1:
        print('      QB'+str(qubit+1)+' -> ', end=' ')
        q = [cirq.NamedQubit(f"QB{j + 1}") for j in [qubit]]
        for j in [0]:#range(5):
            c.append(cirq.X(q[j]))

    elif option == 2:
        q = [cirq.NamedQubit(f"QB{j + 1}") for j in range(5)]
        for j in range(5):
            c.append(cirq.X(q[j]))
    else:
        sys.exit("Option 1 or 2 only")


    if 'Simulator' in str(backend):
        # noise_model = cirq.NoiseModel.from_noise_model_like(cirq.depolarize(p=0.01))
        # moment = cirq.Moment(cirq.X.on_each(q))
        # noisy_moment = noise_model.noisy_moment(moment, system_qubits=q)
        # c = cirq.Circuit(noisy_moment)
        c = c.with_noise(cirq.depolarize(p=0.01))


    c.append(cirq.measure(*q, key="M"))


    run = backend.run(c, repetitions=shots).histogram(key="M")
    if option == 1:
        print(' Success rate ', (run[1]/shots)*100, ' %')
    elif option == 2:
        print('      Success rate ~', ((run[31]/shots)*100**5)**(1/5), ' %')
    else:
        sys.exit("Option 1 or 2 only")


def main():

    args=get_args()

    print('Running on backend = ', args.backend)

    if args.backend == 'simulator':
        backend = cirq.Simulator()
        print("Inducing artificial noise into Simulator with a DepolarizingChannel p=0.01")
        print("See https://quantumai.google/reference/python/cirq/depolarize")

    elif args.backend == 'helmi':
        backend = Helmi().set_helmi()

    else:
        sys.exit("Backend option not recognised")

    
    if args.option == 1:
        print(' ')
        print('   Flip one qubit at a time')
        print(' ')
        for qb in range(5):
            flip_qubits(backend, qb, 1)

    elif args.option == 2:
        print(' ')
        print('   Flip all qubits at once')
        print(' ')
        flip_qubits(backend, None, 2)

    elif args.option == 3:
        print(' ')
        print('   Flip one qubit at a time')
        print(' ')
        for qb in range(5):
            flip_qubits(backend, qb, 1)
        print(' ')
        print('   Flip all qubits at once')
        print(' ')
        flip_qubits(backend, None, 2)

    elif args.option == 4:
        qb=int(args.qubit)
        print(' ')
        print('   Flipping QB'+str(qb+1))
        print(' ')
        flip_qubits(backend, qb, 1)
    else:
        sys.exit("Error in argument options")




    # User can flip one by one
    # Or flip 1 qubit at a time
    # or choose a qubit to flip
    


    


if __name__ == '__main__':
    main()



