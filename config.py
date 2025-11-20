import os
from pathlib import Path
from dotenv import load_dotenv
from nuclia import sdk
import logging

load_dotenv()

KB_URL = os.getenv("KB_URL")
KB_API_KEY = os.getenv("KB_API_KEY")
DATA_DIR = Path(__file__).parent / "data"

logger = logging.getLogger(__name__)

def get_kb_client():
    """
    Get configured Nuclia KB client with environment validation.
    
    Returns the configured client without logging sensitive credentials.
    Raises ValueError if required environment variables are missing.
    """
    if not KB_URL:
        raise ValueError("KB_URL environment variable is required but not set")
    if not KB_API_KEY:
        raise ValueError("KB_API_KEY environment variable is required but not set")
    
    # Initialize client without logging credentials
    sdk.NucliaAuth().kb(url=KB_URL, token=KB_API_KEY)
    logger.info("Nuclia KB client initialized successfully")
    return True
