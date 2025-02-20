# v2/app/main.py

from fastapi import FastAPI
from . import process
# Import your router modules
# Adjust these imports if your directory structure differs
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
    description="An example FastAPI project with multiple routers",
    version="1.0.0"
)

# Include routers with prefixes and tags for better organization
app.include_router(appinfoRouter.router, prefix="/appinfo", tags=["App Info"])
app.include_router(overViewRouter.router, prefix="/overview", tags=["Overview"])
app.include_router(payNowRouter.router, prefix="/paynow", tags=["Pay Now"])
app.include_router(perinfoRouter.router, prefix="/perinfo", tags=["Personal Info"])
app.include_router(sendotpRouter.router, prefix="/sendotp", tags=["Send OTP"])
app.include_router(slotTimeRouter.router, prefix="/slottime", tags=["Slot Time"])
app.include_router(verifyRouter.router, prefix="/verify", tags=["Verify"])




@app.get("/")
def root():
    return {"message": "Hello from FastAPI!"}
