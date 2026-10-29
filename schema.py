import re
from pydantic import BaseModel, Field, ConfigDict, field_validator
class UserCreate(BaseModel):
    username: str= Field(min_length= 4, max_length=20)
    password: str= Field(min_length= 1)
    role: str= Field(default= "user")

    @field_validator("username")
    @classmethod
    def verify_username(cls, value: str) -> str:
        result = re.fullmatch(r"[A-Za-z0-9_]+", value)

        if result is None:
            raise ValueError(
                "Username can contain only letters, numbers, and underscores"
            )

        return value
        

    @field_validator("password")
    @classmethod
    def verify_password(cls, value: str):
        if not any(c.isupper()for c in value):
            raise ValueError("password must contain atleast one uppercase letter")

        if not any(c.islower() for c in value):
            raise ValueError("password must contain atleast one lowercase letter")

        if not any(c.isdigit() for c in value):
            raise ValueError("password must contain atleast one digit")

        return value


class UserResponse(BaseModel):
    model_config= ConfigDict(from_attributes= True)

    id: int
    username: str

class UserLogin(BaseModel):
    username: str
    password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str    



