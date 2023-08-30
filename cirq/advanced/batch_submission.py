"""
This example demonstrates how to submit multiple circuits as a batch using IQMSampler.
"""
import os
import cirq
from cirq_iqm.iqm_sampler import IQMSampler

HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
sampler = IQMSampler(HELMI_CORTEX_URL)

# Create a list to store the circuits

circuit_list = []

# Create 2 example Bell state circuits
q1, q2 = cirq.NamedQubit('Alice'), cirq.NamedQubit('Bob')
circuit1 = cirq.Circuit()
circuit1.append(cirq.H(q1))
circuit1.append(cirq.CNOT(q1, q2))
circuit1.append(cirq.measure(q1, q2, key='m'))

print("Circuit 1")
print(circuit1)


circuit2 = cirq.Circuit()
circuit2.append(cirq.H(q1))
circuit2.append(cirq.CNOT(q2, q1))
circuit2.append(cirq.measure(q1, q2, key='m'))

print("Circuit 2")
print(circuit2)

# Decompose the circuits

decomposed_circuit1 = sampler.device.decompose_circuit(circuit1)

decomposed_circuit2 = sampler.device.decompose_circuit(circuit2)

routed_circuit_1, _, _ = sampler.device.route_circuit(decomposed_circuit1)

routed_circuit_2, _, _ = sampler.device.route_circuit(decomposed_circuit2)

circuit_list.append(routed_circuit_1)
circuit_list.append(routed_circuit_2)

results = sampler.run_iqm_batch(circuit_list, repetitions=100)

for result in results:
    print(result.histogram(key="m"))