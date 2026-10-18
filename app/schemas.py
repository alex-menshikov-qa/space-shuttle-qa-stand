"""Request and response bodies of the JSON API."""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    name: str = Field(examples=["Jane Doe"])
    email: str = Field(examples=["jane.doe@example.com"])
    password: str = Field(examples=["secret123"], description="At least 6 characters")


class LoginRequest(BaseModel):
    email: str = Field(examples=["jane.doe@example.com"])
    password: str = Field(examples=["secret123"])


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class RegisterResponse(UserResponse):
    access_token: str


class LoginResponse(BaseModel):
    id: int
    access_token: str


class OkResponse(BaseModel):
    ok: bool = True
