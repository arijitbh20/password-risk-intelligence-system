from dotenv import load_dotenv
import os

load_dotenv()

FASTAPI_URL = os.getenv("FASTAPI_URL")
DASHBOARD_URL = os.getenv("DASHBOARD_URL")
DATABASE_PATH = os.getenv("DATABASE_PATH")