import json
import os

import requests
from iqm.iqm_client import IQMClient  # Requires iqm_client==15.3
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


Q50_CORTEX_URL = os.getenv('Q50_CORTEX_URL')
if not Q50_CORTEX_URL:
    raise ValueError('Environment variable Q50_CORTEX_URL is not set')

quantum_computer = "q50"
provider = IQMProvider(Q50_CORTEX_URL, quantum_computer=quantum_computer)
backend = provider.get_backend()

calibration_data = get_calibration_data(backend.client)
