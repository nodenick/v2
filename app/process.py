import asyncio
import aiohttp
import re
import random
import json
import logging

from .main import broadcast_sitekey  # We keep broadcast_sitekey
# Remove get_captcha_token since we're reading from tokens.txt

BASE_URL = "http://127.0.0.1:8000"
INITIAL_RETRY_DELAY = 0.2  # seconds

def load_tokens():
    with open("app/tokens.json", "r") as f:
        return json.load(f)

_TOKEN = load_tokens()["_token"]

# Payload definitions
APPINFO_PAYLOAD = {
    "_token": _TOKEN,
    "highcom": "3",
    "webfile_id": "BGDRV18D9525",
    "webfile_id_repeat": "BGDRV18D9525",
    "ivac_id": "2",
    "visa_type": "2",
    "family_count": "0",
    "visit_purpose": "for higher study"
}

PERINFO_PAYLOAD = {
    "_token": _TOKEN,
    "full__name": "MD RASHEDUL ISLAM",
    "email_name": "parosh.cse@gmail.com",
    "pho_ne": "01766283131"
}

OVERVIEW_PAYLOAD = {
    "_token": _TOKEN
}

SENDOTP_PAYLOAD = {
    "_token": _TOKEN,
    "resend": "0"
}

VERIFYOTP_PAYLOAD = {
    "_token": _TOKEN,
    "otp": "465345"  # placeholder; will be updated with user input
}

SLOTTIME_PAYLOAD = {
    "_token": _TOKEN,
    "appointment_date": "2025-02-23"
}

PAYNOW_PAYLOAD = {
    "_token": _TOKEN,
    "appointment_date": "2025-02-23",
    "appointment_time": "10",
    "hash_param": "placeholder_hash"  # will be replaced by reCAPTCHA token from tokens.txt
}

def extract_sitekey(captcha_html: str) -> str:
    """
    Extract the data-sitekey from the captcha HTML.
    Example: <div class="g-recaptcha" data-sitekey="6LdOCpAqAAAAAOLNB3Vwt_H7Nw4GGCAbdYm5Brsb">
    """
    match = re.search(r'data-sitekey="([^"]+)"', captcha_html)
    return match.group(1) if match else None

def read_token_from_file(filepath="tokens.txt") -> str:
    """
    Reads the most recent reCAPTCHA token from a file.
    Returns None if the file doesn't exist or is empty.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            token = f.read().strip()
            return token if token else None
    except FileNotFoundError:
        return None

async def post_with_infinite_retry(session, endpoint: str, data: dict, step_name: str):
    """
    Makes an asynchronous POST request to `endpoint` with `data`.
    Uses exponential backoff with jitter for retries until a 2xx response is received.
    """
    attempt = 1
    delay = INITIAL_RETRY_DELAY
    while True:
        print(f"\n[Attempt #{attempt}] Calling {step_name} endpoint: {endpoint}")
        try:
            async with session.post(endpoint, json=data) as resp:
                if resp.status < 300:
                    try:
                        return await resp.json()
                    except:
                        return await resp.text()
                else:
                    text = await resp.text()
                    print(f"{step_name} step failed (status {resp.status}): {text}")
        except Exception as e:
            print(f"{step_name} step encountered exception: {e}")

        # Exponential backoff with jitter
        sleep_time = delay + random.uniform(0, 0.1)
        print(f"Retrying in {sleep_time:.2f} seconds...")
        await asyncio.sleep(sleep_time)
        delay += 0.2
        attempt += 1

async def run_process():
    async with aiohttp.ClientSession() as session:
        # 1) appinfo
        print("\nNow calling: appinfo")
        await post_with_infinite_retry(session, f"{BASE_URL}/appinfo/apinfo", APPINFO_PAYLOAD, "appinfo")
        print("appinfo step succeeded.")

        # 2) perinfo
        print("\nNow calling: perinfo")
        await post_with_infinite_retry(session, f"{BASE_URL}/perinfo/personal-info-submit", PERINFO_PAYLOAD, "perinfo")
        print("perinfo step succeeded.")

        # 3) overview
        print("\nNow calling: overview")
        await post_with_infinite_retry(session, f"{BASE_URL}/overview/overview-submit", OVERVIEW_PAYLOAD, "overview")
        print("overview step succeeded.")

        # 4) sendotp
        while True:
            print("\nNow calling: sendotp")
            sendotp_resp = await post_with_infinite_retry(session, f"{BASE_URL}/sendotp/pay-otp-sent", SENDOTP_PAYLOAD, "sendotp")
            if isinstance(sendotp_resp, dict) and sendotp_resp.get("success") is True:
                print("sendotp response:", sendotp_resp)
                print("sendotp step succeeded.")
                break
            else:
                print("sendotp returned success=False. Retrying...")
                print("sendotp response:", sendotp_resp)
                await asyncio.sleep(INITIAL_RETRY_DELAY)

        # Ask user for OTP (blocking)
        loop = asyncio.get_running_loop()
        user_otp = await loop.run_in_executor(None, input, "\nEnter the OTP you received: ")

        # 5) verifyotp
        VERIFYOTP_PAYLOAD["otp"] = user_otp
        print("\nNow calling: verifyotp")
        await post_with_infinite_retry(session, f"{BASE_URL}/verify/pay-otp-verify", VERIFYOTP_PAYLOAD, "verifyotp")
        print("verifyotp step succeeded.")

        # 6) slottime
        print("\nNow calling: slottime")
        slottime_resp = await post_with_infinite_retry(session, f"{BASE_URL}/slottime/pay-slot-time", SLOTTIME_PAYLOAD, "slottime")
        print("slottime step succeeded.")

        # Extract siteKey from captcha response HTML
        captcha_html = slottime_resp.get("captcha", "") if isinstance(slottime_resp, dict) else ""
        site_key = extract_sitekey(captcha_html)
        if site_key:
            print(f"🔑 Found siteKey in captcha: {site_key}")

            # 1) Broadcast the siteKey so the browser can render reCAPTCHA
            await broadcast_sitekey(site_key)
        else:
            print("❌ No siteKey found. (Will still check tokens.txt, but likely won't have a valid token.)")

        # 7) paynow
        while True:
            print("\nNow calling: paynow")

            # 2) Wait until we find a token in tokens.txt
            token_from_file = read_token_from_file("tokens.txt")
            while not token_from_file:
                print("❌ No token found in tokens.txt. Waiting 5s for a new token...")
                await asyncio.sleep(5)
                token_from_file = read_token_from_file("tokens.txt")

            print(f"✅ Found token in tokens.txt: {token_from_file}")
            PAYNOW_PAYLOAD["hash_param"] = token_from_file

            paynow_resp = await post_with_infinite_retry(session, f"{BASE_URL}/paynow/paynow", PAYNOW_PAYLOAD, "paynow")
            if isinstance(paynow_resp, dict) and paynow_resp.get("success") is True:
                print("paynow step succeeded.")
                if "url" in paynow_resp:
                    print(f"Redirect URL: {paynow_resp['url']}")
                break
            else:
                message = paynow_resp.get("message", "") if isinstance(paynow_resp, dict) else paynow_resp
                print(f"paynow returned success=False, message='{message}'")

                # If the server complains about an invalid token or validation, let's re-broadcast the siteKey
                if message == "Validation failed. Please try again later." and site_key:
                    print("🔄 Re-broadcasting siteKey. Solve reCAPTCHA again and update tokens.txt with new token.")
                    await broadcast_sitekey(site_key)
                    # Then loop back up, which re-checks tokens.txt in 5s
                else:
                    print("Unknown error or no siteKey to re-broadcast. Exiting paynow step.")
                    break

        print("\nProcess completed successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_process())
