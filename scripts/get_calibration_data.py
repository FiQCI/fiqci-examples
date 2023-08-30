import json
import os

import requests
from iqm_client import IQMClient  # Requires iqm_client==12.5
from qiskit_iqm import IQMProvider


def get_calibration_data(client: IQMClient, calibration_set_id=None, filename: str = None):
    """
    Return the calibration data and figures of merit using IQMClient.
    Optionally you can input a calibration set id (UUID) to query historical results
    Optionally save the response to a json file, if filename is provided
    """
    headers = {'User-Agent': client._signature}
    bearer_token = client._get_bearer_token()
    headers['Authorization'] = bearer_token

    url = os.path.join(client._base_url, 'calibration')
    if calibration_set_id:
        url = os.path.join(url, calibration_set_id)

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # will raise an HTTPError if the response was not ok

    data = response.json()
    data_str = json.dumps(data, indent=4)

    if filename:
        with open(filename, 'w') as f:
            f.write(data_str)
        print(f"Data saved to {filename}")

    return data


HELMI_CORTEX_URL = os.getenv('HELMI_CORTEX_URL')
if not HELMI_CORTEX_URL:
    raise ValueError("Environment variable HELMI_CORTEX_URL is not set")

# Using Qiskit as an example of how to query using this function.

provider = IQMProvider(HELMI_CORTEX_URL)
backend = provider.get_backend()

calibration_data = get_calibration_data(backend.client)

print(calibration_data)
