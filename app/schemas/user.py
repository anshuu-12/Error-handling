import re
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

class UserBase(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Full name of the user (2 to 50 characters)"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    phone: str = Field(
        ...,
        description="10-digit mobile number"
    )
    age: int = Field(
        ...,
        ge=18,
        le=100,
        description="User age must be between 18 and 100"
    )
    status: Literal["active", "inactive"] = Field(
        default="active",
        description="Account status (defaults to active)"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty or just whitespace")
        if any(char.isdigit() for char in cleaned):
            raise ValueError("Name must not contain numbers")
        return cleaned

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.fullmatch(r"^\d{10}$", v):
            raise ValueError("Phone number must be exactly 10 digits (0-9)")
        return v


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=100)
    status: Optional[Literal["active", "inactive"]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Name cannot be empty or just whitespace")
            if any(char.isdigit() for char in cleaned):
                raise ValueError("Name must not contain numbers")
            return cleaned
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.fullmatch(r"^\d{10}$", v):
            raise ValueError("Phone number must be exactly 10 digits (0-9)")
        return v


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)