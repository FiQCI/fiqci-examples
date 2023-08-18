"""
This advanced example demonstrates how one can submit a list if circuits with a parameter sweep.
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

circuit_template = cirq.Circuit([
    cirq.H(q1),
    cirq.CNOT(q1, q2),
    cirq.Z(q1) ** theta,
    cirq.Z(q2) ** theta,
    cirq.CNOT(q1, q2),
    cirq.H(q1),
    cirq.measure(q1, q2, key='m'),
])

# Create a list of cirq.Circuits and their corresponding parameter sweeps
circuit_list = []

num_circuits_in_batch = 5
num_sweeps_in_circuit = 10

# Create each circuit and corresponding parameter sweep
for i in range(num_circuits_in_batch):
    param_sweep = cirq.Linspace(theta.name, start=0, stop=1, length=num_sweeps_in_circuit)
    for param_values in param_sweep:
        # Resolve the parameters for the circuit
        resolved_circuit = cirq.resolve_parameters(circuit_template, param_values)
        decomposed_circuit = device.decompose_circuit(resolved_circuit)
        routed_circuit, _, _ = device.route_circuit(decomposed_circuit)
        simplified_circuit = simplify_circuit(routed_circuit)

        circuit_list.append(simplified_circuit)

# Use run_iqm_batch instead of sampler.run_sweep
results = sampler.run_iqm_batch(circuit_list, repetitions=1000)

for i, result in enumerate(results):
    batch_idx = i // num_sweeps_in_circuit
    sweep_idx = i % num_sweeps_in_circuit
    print(f'Batch #{batch_idx}, Sweep #{sweep_idx}')
    print(result.histogram(key="m", fold_func=fold_func))