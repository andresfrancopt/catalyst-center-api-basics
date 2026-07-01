"""
Catalyst Center - Switches and Hubs Viewer
-------------------------------------------
A pure Python script (no catalystcentersdk) that connects to a Cisco
Catalyst Center instance, authenticates via the REST API, and retrieves
and displays all devices in the 'Switches and Hubs' family.

Dependencies: requests, python-dotenv
Configuration: set CATALYST_USERNAME, CATALYST_PASSWORD, CATALYST_BASE_URL,
               and CATALYST_VERSION in a .env file.
"""

import os
import warnings
warnings.filterwarnings("ignore", message=".*urllib3.*", category=Warning)

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CATALYST_BASE_URL")
USERNAME = os.getenv("CATALYST_USERNAME")
PASSWORD = os.getenv("CATALYST_PASSWORD")
VERSION  = os.getenv("CATALYST_VERSION")


def get_auth_token():
    """Authenticate and return an X-Auth-Token."""
    url = f"{BASE_URL}/dna/system/api/v1/auth/token"
    response = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()
    return response.json()["Token"]


def get_switches(token):
    """Retrieve all devices in the 'Switches and Hubs' family."""
    url = f"{BASE_URL}/dna/intent/api/v1/network-device"
    headers = {"X-Auth-Token": token}
    params  = {"family": "Switches and Hubs"}
    response = requests.get(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
    return response.json().get("response", [])


def print_devices(devices):
    """Print devices in a formatted table."""
    print(f"\n{'HOSTNAME':<50} {'UPTIME'}")
    print("-" * 75)
    for device in devices:
        hostname = device.get("hostname", "N/A")
        uptime   = device.get("upTime", "N/A")
        print(f"{hostname:<50} {uptime}")
    print("-" * 75)
    print(f"Total devices: {len(devices)}\n")


token   = get_auth_token()
devices = get_switches(token)
print_devices(devices)
