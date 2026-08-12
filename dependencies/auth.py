from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.utils.jwt_handler import verify_access_token
from app.database.models import User

O2Auth_scheme = OAuth2PasswordBearer(
    tokenUrl = "/user_login/"
)

async def get_current_user(
        token : str = Depends(O2Auth_scheme),
        db : AsyncSession = Depends(get_db)
):
        user_id = verify_access_token(token)

        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalars().first()

        if not user:
                raise HTTPException(
                        status_code = 404,
                        detail = "User not Found"
                )
        
        return user