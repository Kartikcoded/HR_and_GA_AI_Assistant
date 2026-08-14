"""
client.py
Thin client for ServiceNow's Table API. Isolated from the rest
of the app so it can be tested, mocked, or swapped independently
of the agent logic that calls it.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL")
USERNAME = os.getenv("SERVICENOW_USERNAME")
PASSWORD = os.getenv("SERVICENOW_PASSWORD")
# INSTANCE_URL = "https://dev274611.service-now.com"
# USERNAME = "admin"
# PASSWORD = "V7kl+c4VTnQ="

# ServiceNow's Table API lets you create records in any table via REST.
# "incident" is the standard table for IT/support-style tickets.
INCIDENT_ENDPOINT = f"{INSTANCE_URL}/api/now/table/incident"


class ServiceNowError(Exception):
    """Raised when ServiceNow rejects a request or is unreachable."""
    pass


def create_incident(short_description: str, description: str, urgency: str = "3") -> dict:
    """
    Create an incident in ServiceNow. Returns the created record,
    including its system-generated ticket number.

    urgency: ServiceNow scale, "1" (high) to "3" (low).
    """
    payload = {
        "short_description": short_description,
        "description": description,
        "urgency": urgency,
    }

    try:
        response = requests.post(
            INCIDENT_ENDPOINT,
            auth=(USERNAME, PASSWORD),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        print("ServiceNow response:", response.json())
    except requests.exceptions.RequestException as e:
        raise ServiceNowError(f"Failed to create ServiceNow ticket: {e}") from e

    result = response.json().get("result", {})
    if not result.get("number"):
        raise ServiceNowError("ServiceNow response missing ticket number.")

    return result