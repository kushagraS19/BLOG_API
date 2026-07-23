from fastapi import APIRouter, Depends, HTTPException
from schema.userDTO import Create_user, User_response, AdminDashboardResponse
from database.database import get_db
from database.models import User
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from utils.security import hash_password
from dependencies.permissions import admin_required

user_router = APIRouter(
    prefix = "/user",
    tags = ["User"]
)

@user_router.post("/create", status_code = 201, response_model = User_response)
def register_user(payload : Create_user, db : Session = Depends(get_db)):

    existing = db.query(User).filter(
        User.email == payload.email
    ).first()

    if existing :
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

@user_router.get("/")
def get_all_users(db : Session = Depends(get_db), current_user = Depends(admin_required)):

    all_users = db.query(User).all()

    return {
        "Total" : len(all_users),
        "users" :
          [{
            "id" : user.id,
            "name" : user.name,
            "email" : user.email
            }
        for user in all_users]
    }

@user_router.get("/get_user_by_id/{user_id}", response_model = User_response)
def get_user_by_id(user_id : int ,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = 404,
            detail   = "User not found"
        )
    
    return user

# USER PROFILE -->
@user_router.get("/users/{user_id}")
def user_profile(user_id : int, db : Session = Depends(get_db)):
    user = (
        db.query(User).options(selectinload(User.posts)).filter(User.id == user_id).first()
    )

    if not user:
        raise HTTPException(
            status_code = 404,
            detail = "User not found"
        )

    return {
        "id" : user.id,
        "name" : user.name,
        "email" : user.email,
        "posts" : [
            {
                "post_id" : post.id,
                "title" : post.title,
                "description" : post.description
            }
            for post in user.posts
        ]
    }

# ADMIN DASHBOARD -->
@user_router.get("/admin_dashboard", response_model = list[AdminDashboardResponse])
def admin_dashboard(db : Session = Depends(get_db)):
    users = (
        db.query(User).options(load_only(User.id, User.name),selectinload(User.posts)).order_by(User.id).offset(5).limit(6).all()
    )
    return users