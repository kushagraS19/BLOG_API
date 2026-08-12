from fastapi import APIRouter, Depends, HTTPException, Query
from app.schema.userDTO import Create_user, User_response, AdminDashboardResponse, UserResponseList, User_profile
from app.database.database import get_db
from app.database.models import User
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.security import hash_password
from app.dependencies.permissions import admin_required
import app.services.user_services as user_services
from app.dependencies.auth import get_current_user

user_router = APIRouter(
    prefix = "/user",
    tags = ["User"]
)

@user_router.post("/create", status_code = 201, response_model = User_response)
async def register_user(payload : Create_user, db : Session = Depends(get_db)):

    return await user_services.register_user(
        db,
        payload
    )

@user_router.get("/", response_model = UserResponseList)
async def get_all_users(db : AsyncSession = Depends(get_db), current_user = Depends(admin_required)):
    return await user_services.get_all_users(db=db)

@user_router.get("/get_user_by_id/{user_id}", response_model = User_response)
async def get_user_by_id(user_id : int ,db: AsyncSession = Depends(get_db)):
    return await user_services.get_user_by_id(
        db,
        user_id
    )

# USER PROFILE -->
@user_router.get("/users/{user_id}", response_model = User_profile)
async def user_profile(user_id : int, db : AsyncSession = Depends(get_db)):
    return await user_services.user_profile(
        db,
        user_id
    )

# ADMIN DASHBOARD -->
@user_router.get("/admin_dashboard", response_model = list[AdminDashboardResponse])
async def admin_dashboard(
    db : AsyncSession = Depends(get_db),
    limit : int = Query(10, ge = 0, le = 100),
    offset : int = Query(0),
    current_user = Depends(get_current_user)):

    return await user_services.admin_dashboard(
        db,
        limit,
        offset,
        current_user
    )