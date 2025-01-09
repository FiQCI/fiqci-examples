"""
Two qubit Bell state combinations examples.
Kindly contributed by JLenssen

Generate all 8 possible Bell States on the 5-qubit star layout.
Draw an image comparing error rates between all states.
"""
import collections
import os
import time
from datetime import datetime
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.fake_backends import IQMFakeAdonis
from qiskit_aer import AerSimulator

from qiskit import QuantumCircuit, QuantumRegister, transpile

SIMULATE = False
SHOTS = 1000

state2index = {'00': (0, 0), '10': (1, 0), '11': (1, 1), '01': (0, 1)}


center_qubit = [2]
leaf_qubits = [0, 1, 3, 4]
qubit_combinations = list(product(center_qubit, leaf_qubits)) + \
    list(product(leaf_qubits, center_qubit))

fig, axs = plt.subplots(4, 2, figsize=(10, 10))


n_qubits = 2
qreg = QuantumRegister(n_qubits, "qB")
circuit = QuantumCircuit(qreg)

# Test Circuit
circuit.h(qreg[0])
circuit.cx(qreg[0], qreg[1])
circuit.measure_all()
print(circuit)

backend = IQMFakeAdonis()

if SIMULATE:
    backend = AerSimulator()
else:
    HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
    if not HELMI_CORTEX_URL:
        print("""Environment variable HELMI_CORTEX_URL is not set.
              Are you running on Lumi and on the q_fiqci node?.
              Falling back to fake backend.""")
        # raise ValueError("Environment variable HELMI_CORTEX_URL is not set")

    else:
        provider = IQMProvider(HELMI_CORTEX_URL)
        backend = provider.get_backend()

print(qubit_combinations)
for idx, (qubit_a, qubit_b) in enumerate(qubit_combinations):

    start_time = time.time()
    qubit_mapping = {  # The qubit mapping can be added optionally
        qreg[0]: qubit_a,
        qreg[1]: qubit_b,
    }
    tr_circuit = transpile(
        circuit, backend, optimization_level=0, initial_layout=qubit_mapping,
    )
    job = backend.run(tr_circuit, shots=SHOTS)
    counts = job.result().get_counts()
    end_time = time.time() - start_time

    ordered_counts = collections.OrderedDict(sorted(counts.items()))
    print(f"QB{qubit_a+1}-QB{qubit_b+1} ({end_time:.4f} seconds)")
    print(ordered_counts)

    matrix = np.zeros((2, 2))
    for key in ordered_counts.keys():
        matrix[state2index[key]] = ordered_counts[key]

    im = axs[idx % 4, idx//4].imshow(matrix)
    axs[idx % 4, idx//4].set_title(f"QB{qubit_a}-QB{qubit_b}")
    for (j, i), label in np.ndenumerate(matrix):
        axs[idx % 4, idx//4].text(i, j, int(label), ha='center', va='center')

now = datetime.now()
formatted_date = now.strftime("%d.%m.%Y")
plt.suptitle(
    f"""Bell State experiment ($\\frac{{1}}{{\\sqrt{{2}}}} |00\\rangle + |11\\rangle$) - {
        formatted_date
    }""",
)
plt.tight_layout()
plt.savefig('test.png', dpi=200)
