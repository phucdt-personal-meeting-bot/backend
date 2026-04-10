from pydantic import BaseModel, EmailStr, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least 1 uppercase letter.")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least 1 lowercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least 1 digit.")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool

    model_config = {"from_attributes": True}
