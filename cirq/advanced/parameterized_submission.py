"""
This advanced example demonstrates how to use the run_sweep method to sweep a set of parameters in a circuit
"""
import cirq
from cirq_iqm.iqm_sampler import IQMSampler
import os
import sympy
from cirq_iqm.optimizers import simplify_circuit

from utils import fold_func

HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
sampler = IQMSampler(HELMI_CORTEX_URL)
device = sampler.device

q1, q2 = cirq.NamedQubit('Alice'), cirq.NamedQubit('Bob')

theta = sympy.Symbol("theta")

circuit = cirq.Circuit([
    cirq.H(q1),
    cirq.CNOT(q1, q2),
    cirq.Z(q1) ** theta,
    cirq.Z(q2) ** theta,
    cirq.CNOT(q1, q2),
    cirq.H(q1),
    cirq.measure(q1, q2, key='m'),
])

print(circuit)

decomposed_circuit = device.decompose_circuit(circuit)
routed_circuit, _, _ = device.route_circuit(decomposed_circuit)
simplified_circuit = simplify_circuit(routed_circuit)

params = cirq.Linspace(key="theta", start=0, stop=0.5, length=3)
results = sampler.run_sweep(simplified_circuit, repetitions=1000, params=params)

for result in results:
    print(f'{result.params}: {result.histogram(key="m", fold_func=fold_func)}')