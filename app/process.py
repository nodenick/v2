# # process.py

# import requests
# from app.payloads import (
#     APPINFO_PAYLOAD,
#     PERINFO_PAYLOAD,
#     OVERVIEW_PAYLOAD,
#     SENDOTP_PAYLOAD,
#     VERIFYOTP_PAYLOAD,
#     SLOTTIME_PAYLOAD,
#     PAYNOW_PAYLOAD
# )

# BASE_URL = "http://127.0.0.1:8000"

# def run_process():
#     # 1) Call appinfo
#     print("Calling /appinfo/apinfo ...")
#     resp = requests.post(f"{BASE_URL}/appinfo/apinfo", json=APPINFO_PAYLOAD)
#     if not resp.ok:
#         print(f"appinfo step failed: {resp.text}")
#         return
#     print("appinfo response:", resp.json())

#     # 2) Call perinfo
#     print("\nCalling /perinfo/personal-info-submit ...")
#     resp = requests.post(f"{BASE_URL}/perinfo/personal-info-submit", json=PERINFO_PAYLOAD)
#     if not resp.ok:
#         print(f"perinfo step failed: {resp.text}")
#         return
#     print("perinfo response:", resp.json())

#     # 3) Call overview
#     print("\nCalling /overview/overview-submit ...")
#     resp = requests.post(f"{BASE_URL}/overview/overview-submit", json=OVERVIEW_PAYLOAD)
#     if not resp.ok:
#         print(f"overview step failed: {resp.text}")
#         return
#     print("overview response:", resp.json())

#     # 4) Call sendotp
#     print("\nCalling /sendotp/pay-otp-sent ...")
#     resp = requests.post(f"{BASE_URL}/sendotp/pay-otp-sent", json=SENDOTP_PAYLOAD)
#     if not resp.ok:
#         print(f"sendotp step failed: {resp.text}")
#         return
#     sendotp_data = resp.json()
#     print("sendotp response:", sendotp_data)

#     # Prompt user for OTP if sendotp was successful
#     user_otp = input("\nEnter the OTP you received: ")

#     # 5) Call verifyotp
#     VERIFYOTP_PAYLOAD["otp"] = user_otp  # update the placeholder
#     print("\nCalling /verify/pay-otp-verify ...")
#     resp = requests.post(f"{BASE_URL}/verify/pay-otp-verify", json=VERIFYOTP_PAYLOAD)
#     if not resp.ok:
#         print(f"verifyotp step failed: {resp.text}")
#         return
#     verify_data = resp.json()
#     print("verifyotp response:", verify_data)

#     # 6) Call slottime
#     # If you need a date from the verify response, parse it here
#     # For now, we just use SLOTTIME_PAYLOAD as-is
#     print("\nCalling /slottime/pay-slot-time ...")
#     resp = requests.post(f"{BASE_URL}/slottime/pay-slot-time", json=SLOTTIME_PAYLOAD)
#     if not resp.ok:
#         print(f"slottime step failed: {resp.text}")
#         return
#     slottime_data = resp.json()
#     print("slottime response:", slottime_data)

#     # Prompt user for hash-param if slottime was successful
#     user_hash = input("\nEnter the hash-param: ")

#     # 7) Call paynow
#     PAYNOW_PAYLOAD["hash_param"] = user_hash  # update the placeholder
#     print("\nCalling /paynow/paynow ...")
#     resp = requests.post(f"{BASE_URL}/paynow/paynow", json=PAYNOW_PAYLOAD)
#     if not resp.ok:
#         print(f"paynow step failed: {resp.text}")
#         return
#     paynow_data = resp.json()
#     print("paynow response:", paynow_data)

#     print("\nProcess completed successfully!")


# if __name__ == "__main__":
#     run_process()



import requests
import time
from app.payloads import (
    APPINFO_PAYLOAD,
    PERINFO_PAYLOAD,
    OVERVIEW_PAYLOAD,
    SENDOTP_PAYLOAD,
    VERIFYOTP_PAYLOAD,
    SLOTTIME_PAYLOAD,
    PAYNOW_PAYLOAD
)

BASE_URL = "http://127.0.0.1:8000"
RETRY_DELAY_SECONDS = 0.5  # 500ms

def post_with_infinite_retry(endpoint: str, data: dict, step_name: str):
    """
    Makes a POST request to `endpoint` with `data`.
    If the request fails, it automatically retries indefinitely,
    with a 500ms delay between attempts.
    Returns the successful response.
    """
    attempt = 1
    while True:
        print(f"\n[Attempt #{attempt}] Calling {step_name} endpoint: {endpoint}")
        resp = requests.post(endpoint, json=data)

        if resp.ok:
            print(f"{step_name} step succeeded.")
            return resp
        else:
            print(f"{step_name} step failed (status {resp.status_code}): {resp.text}")
            print(f"Retrying in {RETRY_DELAY_SECONDS*1000:.0f}ms...")
            time.sleep(RETRY_DELAY_SECONDS)
            attempt += 1

def run_process():
    # -------------------------
    # 1) appinfo
    # -------------------------
    resp = post_with_infinite_retry(
        f"{BASE_URL}/appinfo/apinfo",
        APPINFO_PAYLOAD,
        "appinfo"
    )
    print("appinfo response:", safe_json(resp))

    # -------------------------
    # 2) perinfo
    # -------------------------
    resp = post_with_infinite_retry(
        f"{BASE_URL}/perinfo/personal-info-submit",
        PERINFO_PAYLOAD,
        "perinfo"
    )
    print("perinfo response:", safe_json(resp))

    # -------------------------
    # 3) overview
    # -------------------------
    resp = post_with_infinite_retry(
        f"{BASE_URL}/overview/overview-submit",
        OVERVIEW_PAYLOAD,
        "overview"
    )
    print("overview response:", safe_json(resp))

    # -------------------------
    # 4) sendotp
    # -------------------------
    resp = post_with_infinite_retry(
        f"{BASE_URL}/sendotp/pay-otp-sent",
        SENDOTP_PAYLOAD,
        "sendotp"
    )
    sendotp_data = safe_json(resp)
    print("sendotp response:", sendotp_data)

    # -------------------------
    # Prompt user for OTP
    # -------------------------
    user_otp = input("\nEnter the OTP you received: ")

    # -------------------------
    # 5) verifyotp
    # -------------------------
    VERIFYOTP_PAYLOAD["otp"] = user_otp
    resp = post_with_infinite_retry(
        f"{BASE_URL}/verify/pay-otp-verify",
        VERIFYOTP_PAYLOAD,
        "verifyotp"
    )
    verify_data = safe_json(resp)
    print("verifyotp response:", verify_data)

    # -------------------------
    # 6) slottime
    # -------------------------
    resp = post_with_infinite_retry(
        f"{BASE_URL}/slottime/pay-slot-time",
        SLOTTIME_PAYLOAD,
        "slottime"
    )
    slottime_data = safe_json(resp)
    print("slottime response:", slottime_data)

    # -------------------------
    # Prompt user for hash-param
    # -------------------------
    user_hash = input("\nEnter the hash-param: ")

    # -------------------------
    # 7) paynow
    # -------------------------
    PAYNOW_PAYLOAD["hash_param"] = user_hash
    resp = post_with_infinite_retry(
        f"{BASE_URL}/paynow/paynow",
        PAYNOW_PAYLOAD,
        "paynow"
    )
    paynow_data = safe_json(resp)
    print("paynow response:", paynow_data)

    print("\nProcess completed successfully!")

def safe_json(response):
    """Safely parse JSON from the response. If parsing fails, return raw text."""
    try:
        return response.json()
    except:
        return response.text

if __name__ == "__main__":
    run_process()
