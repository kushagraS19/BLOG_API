from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.utils.jwt_handler import verify_access_token
from app.database.models import User

O2Auth_scheme = OAuth2PasswordBearer(
    tokenUrl = "/user_login/"
)

def get_current_user(
        token : str = Depends(O2Auth_scheme),
        db : Session = Depends(get_db)
):
        user_id = verify_access_token(token)

        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
                raise HTTPException(
                        status_code = 404,
                        detail = "User not Found"
                )
        
        return user