
from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if (
            len(value) > 255
            or value.count("@") != 1
            or value.startswith("@")
            or value.endswith("@")
            or "." not in value.rsplit("@", 1)[1]
            or any(char.isspace() for char in value)
        ):
            raise ValueError("Enter a valid email address")
        return value


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
