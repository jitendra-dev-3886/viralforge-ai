from pydantic import BaseModel, EmailStr, ConfigDict


# ------------------------
# Register Request
# ------------------------

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


# ------------------------
# Login Request
# ------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ------------------------
# User Response
# ------------------------

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    is_active: bool
    is_verified: bool


# ------------------------
# Login Response
# ------------------------

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str
    user: UserResponse


# ------------------------
# Register Response
# ------------------------

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user: UserResponse