from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

# ==========================
# JWT Configuration
# ==========================

SECRET_KEY = "viralforge-super-secret-key-change-this-in-production"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 Days


# ==========================
# Password Hashing
# ==========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ==========================
# JWT Token
# ==========================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token


def decode_access_token(token: str):

    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )