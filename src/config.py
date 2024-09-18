from dotenv import load_dotenv
import os

load_dotenv()

RAMP_CLIENT_ID = os.getenv("RAMP_CLIENT_ID")
RAMP_CLIENT_SECRET = os.getenv("RAMP_CLIENT_SECRET")

if not RAMP_CLIENT_ID or not RAMP_CLIENT_SECRET:
    raise ValueError("RAMP_CLIENT_ID and RAMP_CLIENT_SECRET must be set in the environment")
