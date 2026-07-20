import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

# ==========================================
# JWT Configuration
# ==========================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "viralforge-super-secret-key-change-this"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        60 * 24 * 7
    )
)

# ==========================================
# Password Hashing
# ==========================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

# ==========================================
# Hash Password
# ==========================================

def hash_password(password: str) -> str:

    return pwd_context.hash(password)

# ==========================================
# Verify Password
# ==========================================

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )

# ==========================================
# Create Access Token
# ==========================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
):

    to_encode = data.copy()

    expire = (
        datetime.utcnow()
        + (
            expires_delta
            if expires_delta
            else timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )
    )

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt

# ==========================================
# Decode Access Token
# ==========================================

def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except JWTError:

        return None

# ==========================================
# Generate Refresh Token
# ==========================================

def generate_refresh_token():

    import secrets

    return secrets.token_urlsafe(64)

# ==========================================
# Token Expiry Helper
# ==========================================

def get_token_expiry():

    return datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )