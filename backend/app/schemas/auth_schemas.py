from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class LoginIn(BaseModel):
    """
    Schema login đơn giản:
    - identifier: username HOẶC email (tự động detect)
    - password: mật khẩu
    """
    identifier: str = Field(..., min_length=3, description="Username hoặc Email")
    password: str = Field(..., min_length=6, description="Mật khẩu")

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Username/Email không được để trống")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Password không được để trống")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"identifier": "admin11", "password": "admin123"},
                {"identifier": "admin11@example.com", "password": "admin123"}
            ]
        }
    }

class LoginOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshIn(BaseModel):
    refresh_token: str

class RefreshOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class MeOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None = None
    roles: list[str] = Field(default_factory=list)
    role: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}