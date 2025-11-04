"""Pydantic models for request validation."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserRegister(BaseModel):
    """Model for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)
    fullname: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format."""
        if not v.isdigit():
            raise ValueError('Số điện thoại chỉ được chứa chữ số')
        return v


class UserLogin(BaseModel):
    """Model for user login."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class ProfileUpdate(BaseModel):
    """Model for profile update."""
    fullname: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format."""
        if not v.isdigit():
            raise ValueError('Số điện thoại chỉ được chứa chữ số')
        return v


class CartItemUpdate(BaseModel):
    """Model for cart item update."""
    quantity: int = Field(..., ge=1)
