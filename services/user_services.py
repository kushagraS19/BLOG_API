from schema.userDTO import Create_user
from utils.security import hash_password
from database.models import User
from fastapi import  HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload, load_only

# USER REGISTER -->
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

# GET USER BYB ID -->
def get_user_by_id(db : Session, user_id : int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = 404,
            detail = "User not found"
        )

    return user

