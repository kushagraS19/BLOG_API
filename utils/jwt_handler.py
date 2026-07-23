from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import HTTPException

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data : dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp" : expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

def verify_access_token(token : str):
    try : 
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        print(payload)
        user_id = payload.get("sub")

        if user_id is None :
            raise HTTPException(
                status_code = 401,
                detail = "Invalid token"
            )
        
        return user_id
    
    except JWTError :
        raise HTTPException(
            status_code = 401,
            detail = "Invalid token"
        )