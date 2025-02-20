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
import re
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
    If the request fails (HTTP status not OK), it automatically retries indefinitely,
    with a 500ms delay between attempts.
    Returns the successful requests.Response object (HTTP 2xx).
    """
    attempt = 1
    while True:
        print(f"\n[Attempt #{attempt}] Calling {step_name} endpoint: {endpoint}")
        resp = requests.post(endpoint, json=data)

        if resp.ok:
            # HTTP-level success
            return resp
        else:
            # HTTP-level failure
            print(f"{step_name} step failed (status {resp.status_code}): {resp.text}")
            print(f"Retrying in {RETRY_DELAY_SECONDS*1000:.0f}ms...")
            time.sleep(RETRY_DELAY_SECONDS)
            attempt += 1

def run_process():
    # 1) appinfo
    print("\nNow calling: appinfo")
    resp = post_with_infinite_retry(f"{BASE_URL}/appinfo/apinfo", APPINFO_PAYLOAD, "appinfo")
    print("appinfo step succeeded.")

    # 2) perinfo
    print("\nNow calling: perinfo")
    resp = post_with_infinite_retry(f"{BASE_URL}/perinfo/personal-info-submit", PERINFO_PAYLOAD, "perinfo")
    print("perinfo step succeeded.")

    # 3) overview
    print("\nNow calling: overview")
    resp = post_with_infinite_retry(f"{BASE_URL}/overview/overview-submit", OVERVIEW_PAYLOAD, "overview")
    print("overview step succeeded.")

    # 4) sendotp
    print("\nNow calling: sendotp")
    resp = post_with_infinite_retry(f"{BASE_URL}/sendotp/pay-otp-sent", SENDOTP_PAYLOAD, "sendotp")
    print("sendotp step succeeded.")

    # Prompt user for OTP
    user_otp = input("\nEnter the OTP you received: ")

    # 5) verifyotp
    VERIFYOTP_PAYLOAD["otp"] = user_otp
    print("\nNow calling: verifyotp")
    resp = post_with_infinite_retry(f"{BASE_URL}/verify/pay-otp-verify", VERIFYOTP_PAYLOAD, "verifyotp")
    print("verifyotp step succeeded.")

    # 6) slottime
    print("\nNow calling: slottime")
    resp = post_with_infinite_retry(f"{BASE_URL}/slottime/pay-slot-time", SLOTTIME_PAYLOAD, "slottime")
    slottime_data = safe_json(resp)
    print("slottime step succeeded.")

    # Print the siteKey if present in the captcha HTML
    captcha_html = slottime_data.get("captcha", "")
    site_key = extract_sitekey(captcha_html)
    if site_key:
        print(f"Found siteKey in captcha: {site_key}")

    # Prompt user for hash-param
    user_hash = input("\nEnter the hash-param: ")

    # 7) paynow
    while True:
        PAYNOW_PAYLOAD["hash_param"] = user_hash
        print("\nNow calling: paynow")
        resp = post_with_infinite_retry(f"{BASE_URL}/paynow/paynow", PAYNOW_PAYLOAD, "paynow")

        paynow_data = safe_json(resp)
        # Check paynow success
        if paynow_data.get("success") is True:
            # Print the URL
            print("paynow step succeeded.")
            if "url" in paynow_data:
                print(f"Redirect URL: {paynow_data['url']}")
            break
        else:
            # success is false
            message = paynow_data.get("message", "")
            print(f"paynow returned success=False, message='{message}'")
            # If it's specifically "Validation failed. Please try again later."
            # ask for new hash param and retry paynow.
            if message == "Validation failed. Please try again later.":
                print("Please provide a new hash-param to retry paynow.")
                user_hash = input("\nEnter the new hash-param: ")
                continue
            else:
                # If some other error, break or handle differently
                print("Unknown error. Exiting paynow step.")
                break

    print("\nProcess completed successfully!")

def safe_json(response):
    """Safely parse JSON from the response. If parsing fails, return raw text."""
    try:
        return response.json()
    except:
        return response.text

def extract_sitekey(captcha_html: str) -> str:
    """
    Extracts data-sitekey from the captcha HTML if present.
    Example:
      <div class="g-recaptcha" data-sitekey="6LdOCpAqAAAAAOLNB3Vwt_H7Nw4GGCAbdYm5Brsb"> ...
    Returns the sitekey string or None if not found.
    """
    match = re.search(r'data-sitekey="([^"]+)"', captcha_html)
    return match.group(1) if match else None

if __name__ == "__main__":
    run_process()
