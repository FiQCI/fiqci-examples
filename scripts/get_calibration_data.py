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
    headers = {'User-Agent': client._signature}
    bearer_token = client._token_manager.get_bearer_token()
    headers['Authorization'] = bearer_token

    url = os.path.join(
        client._api.iqm_server_url,
        'calibration/metrics/latest',
    )
    if calibration_set_id:
        url = os.path.join(url, calibration_set_id)
    else:
        url = os.path.join(
            client._api.iqm_server_url,
            'calibration/metrics/latest',
        )

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
    raise ValueError(
        'Environment variable HELMI_CORTEX_URL is not set. Are you running on Lumi and on the q_fiqci node?',
    )

# Using Qiskit as an example of how to query using this function.

provider = IQMProvider(HELMI_CORTEX_URL)
backend = provider.get_backend()

calibration_data = get_calibration_data(backend.client)

print(calibration_data)
