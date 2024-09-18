import base64
import requests
from .config import RAMP_CLIENT_ID, RAMP_CLIENT_SECRET

def get_ramp_api_token():
    endpoint = "https://api.ramp.com/developer/v1/token"
    secret = base64.b64encode(f"{RAMP_CLIENT_ID}:{RAMP_CLIENT_SECRET}".encode()).decode()
    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {secret}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    payload = {
        "grant_type": "client_credentials",
        "scope": "accounting:read bills:read business:read merchants:read transactions:read reimbursements:read vendors:read entities:read statements:read",
    }
    response = requests.post(endpoint, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

def get_entities(access_token):
    endpoint = "https://api.ramp.com/developer/v1/entities"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()['data']

def get_bills(access_token, entity_id, cut_off_date_iso8601):
    endpoint = "https://api.ramp.com/developer/v1/bills"
    params = {"entity_id": entity_id, "to_issued_date": cut_off_date_iso8601}
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['data']
