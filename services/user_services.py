from app.schema.userDTO import Create_user
from app.utils.security import hash_password
from app.database.models import User
from fastapi import  HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from app.dependencies.permissions import admin_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# USER REGISTER -->
async def register_user(db : AsyncSession, payload : Create_user):
    result = await db.execute(select(User).where(User.email == payload.email))
    existing = result.scalars().first()

    if existing:
        raise ValueError("Email already exist")

    user = User(
        name = payload.name,
        email = payload.email,
        password = hash_password(payload.password),
        role = "admin"
    )

    try : 
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code = 400,
            detail = "Email already exist"
        )

# GET USER BY ID -->
async def get_user_by_id(db : AsyncSession, user_id : int):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalars().first()
    if not user:
        raise HTTPException(
            status_code = 404,
            detail = "User not found"
        )

    return user

# GET ALL USERS -->
async def get_all_users(db : AsyncSession):

    result = await db.execute(
        select(User)
    )
    users = result.scalars().all()
    print(users)

    return {
        "total_users" : len(users),
        "users" : users
    }

# USER PROFILE -->
async def user_profile(db : AsyncSession, user_id : int):
    user = await db.execute(
        select(User).options(selectinload(User.posts)).where(User.id == user_id)
    )
    user = user.scalars().first()

    if not user:
        raise HTTPException(
            status_code = 404,
            detail = "User not found"
        )

    return user

# ADMIN DASHBOARD -->
async def admin_dashboard(db : AsyncSession, limit : int , offset : int,current_user : User):
    if current_user.role != "admin":
        raise HTTPException(
            status_code = 403,
            detail = "Unauthorized"
        )

    stmt = (select(User)
            .options(load_only(User.id, User.name),
                     selectinload(User.posts))
            .order_by(User.id.asc())
            .offset(offset)
            .limit(limit))

    result = await db.execute(stmt)
    users = result.scalars().all()

    return users