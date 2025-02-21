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
    "webfile_id": "BGDRV01B1025",
    "webfile_id_repeat": "BGDRV01B1025",
    "ivac_id": "2",
    "visa_type": "2",
    "family_count": "0",
    "visit_purpose": "for higher study"
}

# Example payload for perinfo
PERINFO_PAYLOAD = {
    "_token": _TOKEN,
    "full__name": "MD RASHEDUL ISLAM",
    "email_name": "parosh.cse@gmail.com",
    "pho_ne": "01766283131",
    # If you have family fields:
    # "family[1][name]": "SUSHANTO BAPARY",
    # "family[1][webfile_no]": "BGDKV01B1625",
    # "family[1][again_webfile_no]": "BGDKV01B1625",
    # "family[2][name]": "METU RANI",
    # "family[2][webfile_no]": "BGDKV01B1A25",
    # "family[2][again_webfile_no]": "BGDKV01B1A25"
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
    "appointment_date": "2025-02-23"
}

# Example payload for paynow
PAYNOW_PAYLOAD = {
    "_token": _TOKEN,
    "appointment_date": "2025-02-23",
    "appointment_time": "10",
    "hash_param": "dgdfssdgdfgfdg"
}
