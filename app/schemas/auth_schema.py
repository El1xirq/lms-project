from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Any


class RegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)
    role: str

    @field_validator("password")
    @classmethod
    def validate_password_digits(cls, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise ValueError("The password must contain at least 1 digit.")
        return value


    @field_validator("email", mode="before")
    @classmethod
    def validate_email_lower(cls, email: Any) -> Any:
        if isinstance(email, str):
            return email.lower()
        return email

    @field_validator('role')
    def validate_role(cls, v):
        if v not in ['teacher', 'student']:
            raise ValueError('Role must be teacher or student')
        return v


class RegistrationData(BaseModel):
    email: EmailStr
    hashed_password: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = Field(default='Bearer')


class UpdateUserSchema(BaseModel):
    email: EmailStr | None = Field(default=None)
    hashed_password: str | None = Field(default=None)
    role: str | None = Field(default=None)

    @field_validator('role')
    def validate_role(cls, v):
        if v is not None and v not in ['teacher', 'student']:
            raise ValueError('Role must be teacher or student')
        return v
    

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

