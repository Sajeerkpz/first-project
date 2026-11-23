import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from project root
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Server Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-secret-change-this-before-deployment-123456789")
JWT_EXPIRATION_MS = int(os.getenv("JWT_EXPIRATION_MS", "86400000"))  # 24 hours in ms
JWT_EXPIRATION_SECONDS = JWT_EXPIRATION_MS // 1000

# Database Configuration
# Defaults to SQLite for seamless zero-setup execution, or MySQL if specified/accessible.
DEFAULT_SQLITE_PATH = BASE_DIR / "self_study.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    db_user = os.getenv("DB_USERNAME", "root")
    db_pass = os.getenv("MYSQL_ROOT_PASSWORD", "rootpassword")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "self_study_db")
    # If MYSQL_ROOT_PASSWORD is set explicitly and DB_TYPE is mysql, try mysql
    db_type = os.getenv("DB_TYPE", "auto").lower()
    if db_type == "mysql":
        DB_URL = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    else:
        # Default to SQLite for friction-free out-of-the-box local running
        DB_URL = DEFAULT_SQLITE_URL
elif DB_URL.startswith("jdbc:mysql://"):
    # Convert JDBC URL from application.yml if passed directly
    # e.g., jdbc:mysql://localhost:3306/self_study_db -> mysql+pymysql://...
    clean = DB_URL.replace("jdbc:mysql://", "")
    clean = clean.split("?")[0]
    db_user = os.getenv("DB_USERNAME", "root")
    db_pass = os.getenv("MYSQL_ROOT_PASSWORD", "rootpassword")
    DB_URL = f"mysql+pymysql://{db_user}:{db_pass}@{clean}?charset=utf8mb4"

# CORS configuration
CORS_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://localhost",
    "*"
]

