import time
import sqlite3
from functools import wraps
import bcrypt
import jwt
from flask import request, jsonify, g
from .config import JWT_SECRET, JWT_EXPIRATION_SECONDS
from .models import User
from .database import get_db


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def generate_token(user: User) -> str:
    now = int(time.time())
    payload = {
        "sub": user.email,
        "iat": now,
        "exp": now + JWT_EXPIRATION_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def extract_token_from_header() -> str | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    parts = auth_header.strip().split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def get_current_user_from_token(conn: sqlite3.Connection, token: str | None = None) -> User | None:
    if token is None:
        token = extract_token_from_header()
    if not token:
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        return User.from_row(row)
    except (jwt.PyJWTError, Exception):
        return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        conn = get_db()
        try:
            user = get_current_user_from_token(conn)
            if not user:
                return jsonify({"message": "Unauthorized", "detail": "Unauthorized"}), 401
            g.current_user = user
            g.db = conn
            return f(*args, **kwargs)
        finally:
            conn.close()

    return decorated_function


def optional_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        conn = get_db()
        try:
            user = get_current_user_from_token(conn)
            g.current_user = user
            g.db = conn
            return f(*args, **kwargs)
        finally:
            conn.close()

    return decorated_function
