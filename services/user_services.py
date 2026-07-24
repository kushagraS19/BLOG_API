from schema.userDTO import Create_user
from utils.security import hash_password
from database.models import User
from fastapi import  HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload, load_only

def register_user(db : Session, payload : Create_user):
    existing = db.query(User).filter(User.email == payload.email).first()

    if existing:
        raise HTTPException(
            status_code = 400,
            detail = "Email already exist"
        )

    user = User(
        name = payload.name,
        email = payload.email,
        password = hash_password(payload.password),
        role = "user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user