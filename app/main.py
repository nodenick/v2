# # v2/app/main.py

# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
# import asyncio
# import json
# import logging

# # Import your router modules
# from .routers import (
#     appinfoRouter,
#     overViewRouter,
#     payNowRouter,
#     perinfoRouter,
#     sendotpRouter,
#     slotTimeRouter,
#     verifyRouter
# )

# app = FastAPI(
#     title="My FastAPI Application",
#     description="An example FastAPI project with multiple routers + WebSocket",
#     version="1.0.0"
# )

# # Include routers with prefixes and tags
# app.include_router(appinfoRouter.router, prefix="/appinfo", tags=["App Info"])
# app.include_router(overViewRouter.router, prefix="/overview", tags=["Overview"])
# app.include_router(payNowRouter.router, prefix="/paynow", tags=["Pay Now"])
# app.include_router(perinfoRouter.router, prefix="/perinfo", tags=["Personal Info"])
# app.include_router(sendotpRouter.router, prefix="/sendotp", tags=["Send OTP"])
# app.include_router(slotTimeRouter.router, prefix="/slottime", tags=["Slot Time"])
# app.include_router(verifyRouter.router, prefix="/verify", tags=["Verify"])

# # -----------------------------
# # WebSocket Setup
# # -----------------------------

# # Track all active WebSocket connections (the browser)
# active_connections = set()

# # We'll store the latest captcha token here
# latest_recaptcha_token = None

# @app.websocket("/ws/captcha")
# async def captcha_socket(websocket: WebSocket):
#     """
#     WebSocket endpoint for exchanging siteKey (sent by Python)
#     and reCAPTCHA token (sent by the browser).
#     """
#     global latest_recaptcha_token
#     await websocket.accept()
#     active_connections.add(websocket)
#     logging.info("🟢 Browser connected via WebSocket")

#     try:
#         while True:
#             message = await websocket.receive_text()
#             if not message.strip():
#                 continue  # Skip if message is empty
#             try:
#                 data = json.loads(message)
#             except json.JSONDecodeError:
#                 data = message  # Fallback if not valid JSON

#             logging.info(f"Received message: {data}")

#             # If the browser solved reCAPTCHA and sent us the token
#             if isinstance(data, dict) and "token" in data:
#                 latest_recaptcha_token = data["token"]
#                 logging.info(f"✅ Received reCAPTCHA token: {latest_recaptcha_token}")
#     except WebSocketDisconnect:
#         active_connections.remove(websocket)
#         logging.info("🔴 Browser disconnected from WebSocket")

# async def broadcast_sitekey(sitekey: str):
#     """
#     Send the discovered siteKey to all active browser connections
#     so they can inject & render reCAPTCHA.
#     """
#     payload = json.dumps({"siteKey": sitekey})
#     for ws in list(active_connections):
#         try:
#             await ws.send_text(payload)
#         except Exception as e:
#             logging.error(f"Error sending siteKey to a websocket: {e}")

# async def get_captcha_token(timeout=300):
#     """
#     Wait up to `timeout` seconds for the browser to send a token.
#     Returns the token or None if not received in time.
#     """
#     global latest_recaptcha_token
#     for _ in range(timeout):
#         if latest_recaptcha_token:
#             token = latest_recaptcha_token
#             latest_recaptcha_token = None  # Reset after reading
#             return token
#         await asyncio.sleep(1)
#     return None

# @app.get("/broadcast-sitekey")
# async def broadcast_sitekey_http(siteKey: str):
#     """
#     HTTP endpoint to broadcast the siteKey to all connected clients.
#     """
#     await broadcast_sitekey(siteKey)
#     return {"message": f"SiteKey {siteKey} broadcasted!"}

# @app.get("/")
# def root():
#     return {"message": "Hello from FastAPI + WebSocket!"}


# v2/app/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
import logging

# Import your router modules
from .routers import (
    appinfoRouter,
    overViewRouter,
    payNowRouter,
    perinfoRouter,
    sendotpRouter,
    slotTimeRouter,
    verifyRouter
)

app = FastAPI(
    title="My FastAPI Application",
    description="An example FastAPI project with multiple routers + WebSocket",
    version="1.0.0"
)

# Include routers with prefixes and tags
app.include_router(appinfoRouter.router, prefix="/appinfo", tags=["App Info"])
app.include_router(overViewRouter.router, prefix="/overview", tags=["Overview"])
app.include_router(payNowRouter.router, prefix="/paynow", tags=["Pay Now"])
app.include_router(perinfoRouter.router, prefix="/perinfo", tags=["Personal Info"])
app.include_router(sendotpRouter.router, prefix="/sendotp", tags=["Send OTP"])
app.include_router(slotTimeRouter.router, prefix="/slottime", tags=["Slot Time"])
app.include_router(verifyRouter.router, prefix="/verify", tags=["Verify"])

# -----------------------------
# WebSocket Setup
# -----------------------------

# Track all active WebSocket connections (the browser)
active_connections = set()

# We'll store the latest captcha token here (used by get_captcha_token)
latest_recaptcha_token = None

# We'll also store *every* token in a global list for debugging
TOKENS = []

@app.websocket("/ws/captcha")
async def captcha_socket(websocket: WebSocket):
    """
    WebSocket endpoint for exchanging siteKey (sent by Python)
    and reCAPTCHA token (sent by the browser).
    """
    global latest_recaptcha_token
    await websocket.accept()
    active_connections.add(websocket)
    logging.info("🟢 Browser connected via WebSocket")

    try:
        while True:
            message = await websocket.receive_text()
            if not message.strip():
                continue  # Skip if message is empty

            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                data = message  # Fallback if not valid JSON

            logging.info(f"Received message: {data}")

            # If the browser solved reCAPTCHA and sent us the token
            if isinstance(data, dict) and "token" in data:
                latest_recaptcha_token = data["token"]
                logging.info(f"✅ Received reCAPTCHA token: {latest_recaptcha_token}")

                # 1) Overwrite the token file with the new token (delete the previous one)
                with open("tokens.txt", "w", encoding="utf-8") as f:
                    f.write(f"{latest_recaptcha_token}\n")

                # 2) Also store in a global list if you want to keep track in memory
                TOKENS.append(latest_recaptcha_token)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logging.info("🔴 Browser disconnected from WebSocket")

async def broadcast_sitekey(sitekey: str):
    """
    Send the discovered siteKey to all active browser connections
    so they can inject & render reCAPTCHA.
    """
    payload = json.dumps({"siteKey": sitekey})
    for ws in list(active_connections):
        try:
            await ws.send_text(payload)
        except Exception as e:
            logging.error(f"Error sending siteKey to a websocket: {e}")

async def get_captcha_token(timeout=300):
    """
    Wait up to `timeout` seconds for the browser to send a token.
    Returns the token or None if not received in time.
    """
    global latest_recaptcha_token
    for _ in range(timeout):
        if latest_recaptcha_token:
            token = latest_recaptcha_token
            latest_recaptcha_token = None  # Reset after reading
            return token
        await asyncio.sleep(1)
    return None

# -----------------------------
# Utility Endpoints
# -----------------------------

@app.get("/tokens")
def get_tokens():
    """
    Return the list of all tokens received so far.
    (For debugging; don't expose tokens publicly in production.)
    """
    return {"tokens": TOKENS}

@app.get("/broadcast-sitekey")
async def broadcast_sitekey_http(siteKey: str):
    """
    HTTP endpoint to broadcast the siteKey to all connected clients.
    """
    await broadcast_sitekey(siteKey)
    return {"message": f"SiteKey {siteKey} broadcasted!"}

@app.get("/")
def root():
    return {"message": "Hello from FastAPI + WebSocket!"}
