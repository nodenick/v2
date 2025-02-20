from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import cloudscraper
import json
from typing import Dict

router = APIRouter()

# Path to the tokens.json file
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

class ApplicationInfo(BaseModel):
    """
    We no longer ask the user to provide _token.
    That will be loaded from tokens.json.
    """
    highcom: str
    webfile_id: str
    webfile_id_repeat: str
    ivac_id: str
    visa_type: str
    family_count: str
    visit_purpose: str

@router.post("/apinfo")
def submit_application_info(payload: ApplicationInfo):
    """
    Endpoint to send a dynamic payload to the application-info-submit endpoint.
    _token is automatically loaded from tokens.json (not from user input).
    """
    url = "https://payment.ivacbd.com/application-info-submit"
    try:
        tokens = load_tokens()

        # Prepare headers with XSRF token and cookies
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

        # Create a CloudScraper instance
        scraper = cloudscraper.create_scraper()

        # Convert the Pydantic model to a dictionary
        payload_dict = payload.dict()

        # Inject _token from tokens.json into the payload
        payload_dict["_token"] = tokens["_token"]

        # Send the POST request
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
