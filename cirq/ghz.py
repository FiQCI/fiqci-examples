import sys
import argparse
from argparse import RawTextHelpFormatter

from csc_qu_tools.cirq import Helmi
from csc_qu_tools.cirq import add_simulator_noise
import cirq
import numpy as np

"""

This example creates a 5 qubit GHZ stats in cirq

First a Bell state is prepared between QB3 and all the other qubits.
From this we can measure the trace distance between QB3 and each of the other qubits.

A 5 qubit GHZ state is then created 


"""


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

    if args.backend == "simulator":
        device = Helmi()
        backend = cirq.Simulator()

    elif args.backend == "helmi":
        device = Helmi()
        backend = Helmi("settings.json").set_helmi()

    else:
        sys.exit("Backend option not recognised")

    if args.noise == True:
        print("Inducing artificial noise into Simulator with a DepolarizingChannel")
        print("On each Hadamard gate in the circuit")
        print("See https://quantumai.google/reference/python/cirq/depolarize")

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
        c = cirq.Circuit()

        c.append(cirq.H(q[0]))
        c.append(cirq.CNOT(q[0], q[1]))
        c = device.decompose_circuit(circuit=c)

        if args.noise == True:
            c = add_simulator_noise(q, 0.01)

        c.append(cirq.measure(*q, key="M"))
        run = backend.run(c, repetitions=shots).histogram(key="M")
        vd = 0
        fid1 = 0
        for i in range(4):
            vd += np.abs(run[i] / shots - id_dist[i])
            vd = 0.5 * vd
            fid1 += np.sqrt((run[i] / shots) * id_dist[i])

        bell_vd.append(vd)

        if args.verbose == True:
            print(" ")
            print(c)
            print(" ")

        print("Fidelity = ", round(fid1, 3))
        print(offset_2 + offset_3, end=" ")
        print("Distance from target ([0,1]) = ", round(bell_vd[count], 3))

        count += 1

    id_dist = [0 for i in range(32)]
    id_dist[0] = 0.5
    id_dist[31] = 0.5

    q = [cirq.NamedQubit(f"QB{j + 1}") for j in range(5)]
    c = cirq.Circuit()

    c.append(cirq.H(q[2]))
    for qb in [0, 1, 3, 4]:
        c.append(cirq.CNOT(q[2], q[qb]))

    c = device.decompose_circuit(circuit=c)

    if args.noise == True:
        c = add_simulator_noise(q, 0.01)

    c.append(cirq.measure(*q, key="M"))

    run = backend.run(c, repetitions=shots).histogram(key="M")
    vd = 0
    fid2 = 0
    for i in range(32):
        vd += np.sum(np.abs(run[i] / shots - id_dist[i]))
        vd = 0.5 * vd
        fid2 += np.sqrt((run[i] / shots) * id_dist[i])

    print(" ")
    print(offset + "================================ ")
    print(offset + "    Preparing a GHZ-5 State")
    print(offset + "================================ ")
    print(" ")

    if args.verbose == True:
        print(" ")
        print(c)

    print(offset_2 + "GHZ-5 -> Fidelity = ", round(fid2, 3))
    print(offset_2 + "GHZ-5 -> Distance from target ([0,1]) = ", round(vd, 3))

    print(" ")
    print(" ")


if __name__ == "__main__":
    main()
