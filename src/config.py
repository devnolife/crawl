"""
SkillPulse AI - Configuration
Loads environment variables and provides configuration constants
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Application configuration from environment variables"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
    
    # API Keys
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # Database/Storage
    LEARNING_DATA_PATH = os.getenv(
        "LEARNING_DATA_PATH", 
        str(DATA_DIR / "learning_data.json")
    )
    EXPORT_DATA_PATH = os.getenv(
        "EXPORT_DATA_PATH", 
        str(DATA_DIR / "exports")
    )
    
    # Scraping
    USE_SELENIUM = os.getenv("USE_SELENIUM", "false").lower() == "true"
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "2"))
    
    # NLP Models
    TORCH_DEVICE = os.getenv("TORCH_DEVICE", "cpu")
    HF_CACHE_DIR = os.getenv("HF_CACHE_DIR", str(MODELS_DIR / "cache"))
    
    # App
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Makassar")
    DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "IDR")
    USD_TO_IDR = float(os.getenv("USD_TO_IDR", "15800"))
    
    @classmethod
    def ensure_directories(cls):
        """Create required directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        (cls.DATA_DIR / "exports").mkdir(exist_ok=True)
        cls.MODELS_DIR.mkdir(exist_ok=True)
        (cls.MODELS_DIR / "cache").mkdir(exist_ok=True)
    
    @classmethod
    def is_firecrawl_configured(cls) -> bool:
        """Check if Firecrawl API key is configured"""
        return bool(cls.FIRECRAWL_API_KEY and cls.FIRECRAWL_API_KEY != "fc-YOUR_API_KEY_HERE")
    
    @classmethod
    def is_huggingface_configured(cls) -> bool:
        """Check if HuggingFace token is configured"""
        return bool(cls.HUGGINGFACE_TOKEN and cls.HUGGINGFACE_TOKEN != "hf_YOUR_TOKEN_HERE")


# Ensure directories exist on import
Config.ensure_directories()


# For backward compatibility
config = Config()
