import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv(
    "GOOGLE_API_KEY",
    ""
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

ADMIN_TOKEN = os.getenv(
    "ADMIN_TOKEN",
    "fitbuddy-admin"
)

DEMO_MODE = os.getenv(
    "DEMO_MODE",
    "true"
).lower() == "true"