from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict
import cloudscraper
import json

router = APIRouter()

# Path to the tokens.json file (adjust if needed)
TOKENS_FILE_PATH = "app/tokens.json"

def load_tokens() -> Dict[str, str]:
    """
    Load tokens from the tokens.json file.
    """
    try:
        with open(TOKENS_FILE_PATH, "r") as file:
            tokens = json.load(file)
            return tokens
    except FileNotFoundError:
        raise Exception("Tokens file not found. Please create a 'tokens.json' file.")
    except json.JSONDecodeError:
        raise Exception("Tokens file is not a valid JSON.")

# Define the default selected payment details as provided by the backend.
DEFAULT_SELECTED_PAYMENT = {
    "selected_payment[name]": "VISA",
    "selected_payment[slug]": "visacard",
    "selected_payment[link]": "https://securepay.sslcommerz.com/gwprocess/v4/image/gw1/visa.png"
}

class PayNowRequest(BaseModel):
    """
    Removed _token from the user payload.
    We'll load _token from tokens.json automatically.
    """
    appointment_date: str  # Expected format: YYYY-MM-DD
    appointment_time: str  # e.g., "10"
    hash_param: str
    selected_payment_name: Optional[str] = Field(None, alias="selected_payment[name]")
    selected_payment_slug: Optional[str] = Field(None, alias="selected_payment[slug]")
    selected_payment_link: Optional[str] = Field(None, alias="selected_payment[link]")

@router.post("/paynow")
def pay_now(payload: PayNowRequest):
    """
    Endpoint to initiate the payment process.
    
    The user provides appointment_date, appointment_time, and hash_param.
    If the selected payment details are not provided, default values (VISA, visacard, and the corresponding link)
    will be inserted automatically. _token is injected from tokens.json at runtime.
    """
    url = "https://payment.ivacbd.com/paynow"
    try:
        # 1. Load tokens
        tokens = load_tokens()

        # 2. Prepare headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "*/*",
            "Origin": "https://payment.ivacbd.com",
            "Referer": "https://payment.ivacbd.com/payment",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/132.0.0.0 Safari/537.36"
            ),
            "x-requested-with": "XMLHttpRequest",
            "X-XSRF-TOKEN": tokens.get("xsrf_token", ""),
            "Cookie": tokens.get("cookie", ""),
        }

        # 3. Create a CloudScraper instance
        scraper = cloudscraper.create_scraper()

        # 4. Convert the Pydantic model to a dict using aliases for the field names
        payload_dict = payload.dict(by_alias=True)

        # 5. Insert default payment details if not provided
        if not payload_dict.get("selected_payment[name]"):
            payload_dict["selected_payment[name]"] = DEFAULT_SELECTED_PAYMENT["selected_payment[name]"]
        if not payload_dict.get("selected_payment[slug]"):
            payload_dict["selected_payment[slug]"] = DEFAULT_SELECTED_PAYMENT["selected_payment[slug]"]
        if not payload_dict.get("selected_payment[link]"):
            payload_dict["selected_payment[link]"] = DEFAULT_SELECTED_PAYMENT["selected_payment[link]"]

        # 6. Inject _token from tokens.json
        payload_dict["_token"] = tokens["_token"]

        # 7. Send the POST request to the paynow endpoint
        response = scraper.post(url, data=payload_dict, headers=headers)

        if response.status_code == 200:
            try:
                return response.json()
            except Exception:
                return {"message": response.text}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Request failed: {response.text}"
            )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
