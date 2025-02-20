from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict
import cloudscraper
import json

router = APIRouter()

# Path to the tokens.json file (adjust the path if needed)
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

class PersonalInfo(BaseModel):
    """
    No longer requires _token from the user.
    We'll inject _token from tokens.json at runtime.
    """
    full__name: str
    email_name: str
    pho_ne: str
    family_1_name: Optional[str] = Field(None, alias="family[1][name]")
    family_1_webfile_no: Optional[str] = Field(None, alias="family[1][webfile_no]")
    family_1_again_webfile_no: Optional[str] = Field(None, alias="family[1][again_webfile_no]")

@router.post("/personal-info-submit")
def submit_personal_info(payload: PersonalInfo):
    """
    Endpoint to submit personal information.
    
    The payload is provided by the user when calling this API. The family-related fields are optional.
    _token is automatically injected from tokens.json (not user input).
    """
    url = "https://payment.ivacbd.com/personal-info-submit"
    
    try:
        # 1. Load tokens from tokens.json
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

        # 4. Convert the Pydantic model to a dict using aliases
        payload_dict = payload.dict(by_alias=True)

        # 5. Inject _token from tokens.json
        payload_dict["_token"] = tokens["_token"]

        # 6. Send the POST request
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
