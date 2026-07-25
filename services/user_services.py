from schema.userDTO import Create_user
from utils.security import hash_password
from database.models import User
from fastapi import  HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from dependencies.permissions import admin_required

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
        role = "admin"
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

# GET ALL USERS -->
def get_all_users(db : Session):
    users = db.query(User).all()

    return {
        "total_users" : len(users),
        "users" : [
            {
                'user_id' : id,
                'name' : name,
                'email' : email
            }
            for id, name, email in users
        ]
    }

# USER PROFILE -->
def user_profile(db : Session, user_id : int):
    user = (
        db.query(User).options(selectinload(User.posts)).filter(User.id == user_id).first()
    )

    if not user:
        raise HTTPException(
            status_code = 404,
            detail = "User not found"
        )

    return {
        "id" : user_id,
        "name" : user.name,
        "email" : user.email,
        "posts" : [
            {
                "id" : post.id,
                "title" : post.title,
                "description" : post.description
            }
            for post in user.posts
        ]
    }

# ADMIN DASHBOARD -->
def admin_dashboard(db : Session, limit : int , offset : int,current_user : User):
    if current_user.role != "admin":
        raise HTTPException(
            status_code = 403,
            detail = "Unauthorized"
        )

    users = (
        db.query(User)
        .options(load_only(User.id, User.name),selectinload(User.posts))
        .order_by(User.id)
        .limit(limit)
        .offset(offset)
        .all()
    )

    return users