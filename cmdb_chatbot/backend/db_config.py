import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PSSWRD = os.getenv("DB_PASSWORD")  # Get from .env
DB_PORT = int(os.getenv("DB_PORT", "5433"))
SCHEMA = os.getenv("DB_SCHEMA", "general")
