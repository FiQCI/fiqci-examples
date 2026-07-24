import json
import os
import sys

import requests
from iqm.iqm_client import IQMClient
from iqm.qiskit_iqm import IQMProvider


def get_calibration_data(client: IQMClient, calibration_set_id=None, filename: str = None):
    """
    Return the calibration data and figures of merit using IQMClient.
    Optionally you can input a calibration set id (UUID) to query historical results
    Optionally save the response to a json file, if filename is provided
    """
    headers = {"User-Agent": client._iqm_server_client._signature}
    bearer_token = client._iqm_server_client._auth_header_callback()
    headers["Authorization"] = bearer_token

    server_client = client._iqm_server_client
    root_url = server_client.root_url
    quantum_computer = server_client.quantum_computer

    if calibration_set_id:
        url = f"{root_url}/api/devices/{quantum_computer}/calibration/metrics/{calibration_set_id}"
    else:
        url = f"{root_url}/api/devices/{quantum_computer}/calibration/metrics/latest"

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # will raise an HTTPError if the response was not ok

    data = response.json()
    data_str = json.dumps(data, indent=4)

    if filename:
        with open(filename, "w") as f:
            f.write(data_str)
        print(f"Data saved to {filename}")

    return data


def _choose_target(arg: str):
    key = arg.lower()
    if key == 'q50':
        return os.getenv('Q50_CORTEX_URL'), 'q50'
    if key == 'q20':
        return os.getenv('Q20_CORTEX_URL'), 'radiance20'
    raise ValueError("Invalid target. Choose one of: q20, q50")


if len(sys.argv) < 2:
    raise ValueError('Usage: get_calibration_data.py <q20|q50|radiance20>')

url_env, quantum_computer = _choose_target(sys.argv[1])
if not url_env:
    raise ValueError('Environment variable for chosen target is not set')

provider = IQMProvider(url_env, quantum_computer=quantum_computer)
backend = provider.get_backend()

filename = "cals.json"

calibration_data = get_calibration_data(backend.client, filename=filename)
