from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated


Username = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)]
Password = Annotated[str, Field(min_length=8, max_length=128)]


class UserCreateRequest(BaseModel):
    username: Username
    password: Password


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class TokenValidationResponse(BaseModel):
    valid: bool = True
    user: UserResponse