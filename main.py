from fastapi import FastAPI, Depends, HTTPException, status
from database import get_db
from model import User, RevokedToken
from schema import UserCreate, UserResponse, UserLogin, ChangePassword
from security import hash_password, verify_password, create_access_token, get_current_user, get_current_admin
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from security import create_refresh_token, get_user_from_refresh_token, oauth2_scheme
from security import required_role

dbSession = Annotated[Session, Depends(get_db)]
current_user= Annotated[User, Depends(get_current_user)]

app= FastAPI()

@app.post("/register", response_model= UserResponse)
def register(
    user: UserCreate,
    db: dbSession
):
    stmt= select(User).where(
        User.username== user.username
    )
    existing_user= db.scalar(stmt)

    if existing_user:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail= "user already exist"
        )
    hashed_password= hash_password(user.password)

    new_user= User(
        username= user.username,
        password_hash= hashed_password,
        role="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: dbSession
):
    stmt= select(User).where(
        User.username== form_data.username
    )
    existing_user= db.scalar(stmt)
    if not existing_user:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "the user is not found"
        )

    if not verify_password(
        form_data.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail= "password incorrect"
        )
    token1= create_access_token(existing_user.id)
    token2= create_refresh_token(existing_user.id)

    return{
        "access_token": token1,
        "refresh_token": token2,
        "token_type": "bearer"
    }

@app.get("/protected")
def get_user(
    db: dbSession,
    c_user: current_user,
):
    return {
        "mess": "you are authenticated",
        "user_id": c_user.id,
        "user_name": c_user.username,
    }

@app.get("/users/{id}")
def get_user(
    db: dbSession,
    id: int,
    c_user: current_user
):
    if id!= c_user.id:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= "you have no access to another account"
        )
    return {
        "id": c_user.id,
        "username": c_user.username
    }

@app.get("/admin")
def get_admin(
    admin: Annotated[User, Depends(get_current_admin)]
):
    return admin

@app.post("/admin/users/{id}/promote")
def promote_admin(
    id: int,
    db: dbSession,
    admin: Annotated[User, Depends(get_current_admin)]
):
    user= db.get(User, id)
    if user is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "id not found"
        )

    user.role= "admin"

    db.commit()
    db.refresh(user)

    return {
        "message": "promoted",
        "username": user.username,
        "role": user.role
    }
from pydantic import BaseModel

class RefreshRequest(BaseModel):
    refresh_token: str


@app.post("/refresh")
def refresh_access_token(
    data: RefreshRequest,
    db: dbSession
):
    user_id= get_user_from_refresh_token(data.refresh_token)
    user= db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "user id invalid"
        )
    new_access_token= create_access_token(user.id)
    new_refresh_token= create_refresh_token(user.id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "type": "bearer"
    }

@app.put("/change-password")
def change_password(
    data: ChangePassword,
    db: dbSession,
    user: Annotated[User, Depends(get_current_user)]
):
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "old password not valid"
        )

    user.password_hash= hash_password(data.new_password)
    db.commit()

    return {
        "message": "successfully updated"
    }

@app.post("/logout")
def logout(
    db: dbSession,
    user: current_user,
    token= Annotated[str, Depends(oauth2_scheme)]  
):
    revoked_token= RevokedToken(token= token)

    db.add(revoked_token)
    db.commit()

    return {
        "message": "successfully logged out"
    }
@app.get("/admin_only")
def admin_only(
    user: Annotated[User, Depends(required_role("admin"))]
):
    return {
        "message": "you are an admin"
    }


    

    


    


 
