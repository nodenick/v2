# You can hardcode your token here or load it dynamically (e.g., from tokens.json)
import json

def load_tokens():
    with open("app/tokens.json", "r") as f:
        return json.load(f)

_TOKEN = load_tokens()["_token"]


# Example payload for appinfo
APPINFO_PAYLOAD = {
    "_token": _TOKEN,
    "highcom": "3",
    "webfile_id": "BGDRV175B225",
    "webfile_id_repeat": "BGDRV175B225",
    "ivac_id": "2",
    "visa_type": "6",
    "family_count": "0",
    "visit_purpose": "for a vacation"
}

# Example payload for perinfo
PERINFO_PAYLOAD = {
    "_token": _TOKEN,
    "full__name": "Salman farsi",
    "email_name": "salman.farsi4646@outlook.com",
    "pho_ne": "01729469778",
    # If you have family fields:
    # "family[1][name]": "Jane Doe",
    # "family[1][webfile_no]": "123",
    # "family[1][again_webfile_no]": "123"
}

# Example payload for overview
OVERVIEW_PAYLOAD = {
    "_token": _TOKEN
}

# Example payload for sendotp
SENDOTP_PAYLOAD = {
    "_token": _TOKEN,
    "resend": "0"
}

# Placeholder payload for verifyotp
VERIFYOTP_PAYLOAD = {
    "_token": _TOKEN,
    "otp": "465345"
}

# Example payload for slottime
SLOTTIME_PAYLOAD = {
    "_token": _TOKEN,
    "appointment_date": "2025-02-20"
}

# Example payload for paynow
PAYNOW_PAYLOAD = {
    "_token": _TOKEN,
    "appointment_date": "2025-02-20",
    "appointment_time": "10",
    "hash_param": "dgdfssdgdfgfdg"
}
