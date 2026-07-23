from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from utils.security import verify_password
from utils.jwt_handler import create_access_token

auth_router = APIRouter(
    prefix = "/user_login",
    tags = ["Login"]
)

@auth_router.post("/")
def user_login(db : Session = Depends(get_db), form_data : OAuth2PasswordRequestForm = Depends()):
    
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid username"
        )
    
    if not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code = 401,
            detail = "Invalid password"
        )
    
    token = create_access_token(
        {
            "sub" : str(user.id)
        }
    )

    return {
        "access_token" : token,
        "token_type" : "bearer"
    }