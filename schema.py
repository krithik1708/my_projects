from pydantic import BaseModel, Field, ConfigDict

class UserCreate(BaseModel):
    username: str= Field(min_length= 4, max_length=20)
    password: str= Field(min_length= 1)
    role: str= Field(default= "user")

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



