import os
import json
import requests

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import execute
from qiskit_iqm import IQMProvider


def get_calibration_data(calibration_set_id=None, filename: str = None):
    """
    Return the calibration data and figures of merit.
    Optionally you can input a calibration set id (UUID) to query historical results
    Optionally save the response to a json file, if filename is provided
    """
    if not (helmi_cortex_url := os.getenv('HELMI_CORTEX_URL')):
        raise ValueError("Environment variable 'HELMI_CORTEX_URL' is not set")

    if not (iqm_tokens_file := os.getenv('IQM_TOKENS_FILE')):
        raise ValueError("Environment variable 'IQM_TOKENS_FILE' is not set")

    # read token
    try:
        with open(iqm_tokens_file, 'r') as token_file:
            token = json.load(token_file)['access_token']
    except Exception as e:
        raise Exception("Failed to read or parse token file: ", e)

    headers = {'Authorization': "Bearer " + token}

    url = helmi_cortex_url + "/calibration"

    if calibration_set_id:
        url += "/" + calibration_set_id

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return f"Not authenticated. Status code: {response.status_code}"

    data = response.json()
    data_str = json.dumps(data, indent=4)

    if filename:
        with open(filename, 'w') as f:
            f.write(data_str)
        print(f"Data saved to {filename}")

    return data_str


shots = 1000

qreg = QuantumRegister(2, "QB")
creg = ClassicalRegister(2, "C")
circuit = QuantumCircuit(qreg, creg)

circuit.h(qreg[0])
circuit.cx(qreg[0], qreg[1])
circuit.measure_all()

# Uncomment if you wish to print the circuit
# print(circuit.draw())

# Qiskit uses 0 indexing for identifying qubits
qubit_mapping = {
    qreg[0]: 0,  # Map first qubit in Quantum Register to QB1
    qreg[1]: 2,  # Map second qubit in Quantum Register to QB3
}

HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
if not HELMI_CORTEX_URL:
    raise ValueError("Environment variable HELMI_CORTEX_URL is not set")

print(get_calibration_data(calibration_set_id=None, filename=None))

provider = IQMProvider(HELMI_CORTEX_URL)
backend = provider.get_backend()

# Retrieving backend information
# print(f'Native operations: {backend.operation_names}')
# print(f'Number of qubits: {backend.num_qubits}')
# print(f'Coupling map: {backend.coupling_map}')

job = execute(circuit, backend, shots=shots, initial_layout=qubit_mapping)
result = job.result()
exp_result = job.result()._get_experiment(circuit)
# You can retrieve the job at a later date with backend.retrieve_job(job_id)
# Comment out the following lines to get more information about your submitted job
print("Job ID: ", job.job_id())
# print(result.request.circuits)
print("Calibration Set ID: ", exp_result.calibration_set_id)
# print(result.request.qubit_mapping)
# print(result.request.shots)

counts = result.get_counts()
print(counts)
