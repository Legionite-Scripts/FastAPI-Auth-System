from pydantic import BaseModel, EmailStr, Field


class BaseSchema(BaseModel):
    class Config:
        extra = "forbid"  # Prevent extra fields from being accepted


# Signup request schema
class SignupRequest(BaseSchema):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


# Login request schema
class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


# Forgot password request schema
class ForgotPasswordRequest(BaseSchema):
    email: str
