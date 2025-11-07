import os
from pathlib import Path
from dotenv import load_dotenv
from nuclia import sdk

load_dotenv()

KB_URL = os.getenv("KB_URL")
KB_API_KEY = os.getenv("KB_API_KEY")
DATA_DIR = Path(__file__).parent / "data"

sdk.NucliaAuth().kb(url=KB_URL, token=KB_API_KEY)
