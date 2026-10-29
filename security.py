from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from model import User, RevokedToken
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Annotated
import jwt

from config import secret_key, enviroment, url


oauth2_scheme= OAuth2PasswordBearer(tokenUrl= "login")


algorithm= "HS256"

password_hash= PasswordHash.recommended()

def hash_password(
        password: str
):
    return password_hash.hash(password)

def verify_password(
        password: str,
        hashed_password: str
):
    return password_hash.verify(
        password,
        hashed_password
    )

def create_access_token(
        user_id: int
):
    payload= {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes= 240)
    }
    return jwt.encode(
        payload= payload,
        key= secret_key,
        algorithm= algorithm
    )


def create_refresh_token(
        user_id: int
):
    payload= {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(hours= 24)
    }
    return jwt.encode(
        payload= payload,
        key= secret_key,
        algorithm= algorithm
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    print("STEP 1: Bearer token received")

    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
        )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail= "invalid token type"
            )
        
        print("STEP 2: Token decoded successfully")

        revoked= db.scalar(select(RevokedToken).where(
            RevokedToken.token== token
        ))

        if revoked:
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail= "you are logged out, please log in"
            )

        user_subject = payload.get("sub")
        print("STEP 3: Token subject:", user_subject)

        if not isinstance(user_subject, str) or not user_subject.isdigit():
            print("ERROR: Invalid subject")
            raise HTTPException(
                status_code=401,
                detail="Invalid token subject",
            )

        user_id = int(user_subject)

    except jwt.ExpiredSignatureError:
        print("ERROR: Token expired")
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError as e:
        print("JWT ERROR:", repr(e))
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)

    if user is None:
        print("ERROR: User ID not found in database:", user_id)
        raise HTTPException(status_code=401, detail="User not found")

    print("STEP 4: User found successfully")
    return user

def get_current_admin(
        c_user: Annotated[User, Depends(get_current_user)]
):
    if c_user.role != "admin":
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= "you are not an admin"
        )
    return c_user

def get_user_from_refresh_token(
        token: str
):
    try:
        payload= jwt.decode(
            token,
            secret_key,
            algorithm
        )
        if payload.get("type")!= "refresh":
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail= "invalid token"
            )
        user_id= payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail= "user_id not found"
            )
        return int(user_id)
    except(jwt.InvalidTokenError, ValueError):

        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid or expired token"
        )


def required_role(*all_roles: str):
    def check_role(
            user: User= Depends(
                get_current_user
            )
    ):
        if user.role not in all_roles:
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail= "your role is not appropriate"
            )

        return user
    return check_role

     
