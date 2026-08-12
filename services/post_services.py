from sqlalchemy.orm import Session, joinedload
from app.schema.postDTO import Create_post, PostListResponse, PostWithUserResponse, PostPerUser, Post_update, PostResponse, PostSummaryResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Post
from app.database.models import User
from sqlalchemy import asc, desc, or_ , func, select
from fastapi import HTTPException

# CREATE POST -->
async def create_post(db : AsyncSession, payload : Create_post, current_user : User):

    post = Post(
        title = payload.title,
        description = payload.description,
        user_id = current_user.id
    )

    db.add(post)
    await db.commit()
    await db.refresh(post)

    return post

# GET ALL POSTS -->
async def get_all_posts(
        db : Session,
        title : str | None,
        user_id : int | None,
        search : str | None,
        sort_by : str,
        order : str,
        limit : int,
        offset : int
):
    stmt = select(Post)
    count_stmt = select(func.count()).select_from(Post)
    count = await db.execute(count_stmt)
    total_posts = count.scalar_one()
    
    if title:
            stmt = stmt.where(Post.title.ilike(f"%{title}%"))
    
    if user_id:
            stmt = stmt.where(Post.user_id == user_id)
    
    if search:
            stmt = stmt.where(
                or_(
                    Post.title.ilike(f"%{search}%"),
                    Post.description.ilike(f"%{search}%")
                )
            )
    
    column = getattr(Post, sort_by)
    
    stmt = stmt.order_by(
            asc(column) if order == "asc" else desc(column)
        )
    
    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    posts = result.scalars().all()
    
    return PostListResponse(
            total_posts = total_posts,
            limit = limit,
            offset = offset,
            posts = posts
        )

# GET POST WITH USER -->
async def get_post_with_user(db : AsyncSession):
      stmt = (select(Post).options(joinedload(Post.user)))
      result = await db.execute(stmt)
      posts = result.scalars().all()

      return [
            PostWithUserResponse(
            id = post.id,
            title = post.title,
            description = post.description,
            author = post.user.name,
            author_email = post.user.email
      )
      for post in posts
      ]

# POSTS PER USER -->
async def posts_per_user(db : AsyncSession):
      print("before")
      stmt = (select(User.name,func.count(Post.id)).outerjoin(Post).group_by(User.name))
      result = await db.execute(stmt)
      posts = result.all()

      return [
            PostPerUser(
            name = name,
            total_posts = total
      )
      for name, total in posts
      ]

# USERS WHO HAVE ATLEAST 2 POSTS WITH PYTHON IN ITS TITLE -->
async def active_users(db : AsyncSession):
      stmt = (select(
            User.id, 
            User.name,
            func.count(Post.id).label("total_posts")
            ).join(User)
            .group_by(User.id, User.name)
            .having(func.count(Post.id) >= 1)
            .order_by(User.id)
            )
      result = await db.execute(stmt)
      users = result.all()
      
      return [
            {
                  "user_id" : id,
                  "user_name" : name,
                  "total_posts" : total
            }
            for id, name, total in users
      ]

# GET POST BY ID -->
async def get_post_by_id(db : AsyncSession, post_id : int):
      stmt = select(Post).where(Post.id == post_id)
      result = await db.execute(stmt)
      post = result.scalars().first()

      if not post:
            raise HTTPException(
                  status_code = 404,
                  detail = "Post not found"
            )

      return post

# DELETE A POST -->
async def delete_post(db : AsyncSession, post_id : int, current_user : User):
      result = await db.execute(
            select(Post).where(Post.id == post_id)
      )
      post = result.scalars().first()

      if post.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                  status_code = 403,
                  detail = "Unauthorized"
            )

      if not post:
            raise HTTPException(
                  status_code = 404,
                  detail = "Post not found"
            )

      await db.delete(post)
      await db.commit()

      return {
            "message" : "Post deleted successfully",
            "post" : post
      }

# UPDATE POST -->
async def update_post(db : AsyncSession, post_id : int, payload : Post_update, current_user : User):
      result = await db.execute(
            select(Post).where(Post.id == post_id)
      )
      post = result.scalars().first()

      if post.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                  status_code = 403,
                  detail = "Unauthorized"
            )

      if not post:
            raise HTTPException(
                  status_code = 404,
                  detail = "Post not found"
            )

      updates = payload.model_dump(exclude_unset = True)

      for key, value in updates.items():
            setattr(post, key, value)

      await db.commit()
      await db.refresh(post)

      return PostResponse(
            id = post.id,
            title = post.title,
            description = post.description
      )

# ALL USERS STATS -->
async def all_users_stats(db : AsyncSession):
      result = await db.execute(
            select(User.id,User.name, func.count(Post.id))
            .outerjoin(Post)
            .group_by(User.id, User.name)
            .order_by(User.id)
      )
      stats = result.all()

      return [
            {
                  "user_id" : id,
                  "name" : name,
                  "total_posts" : total
            }
            for id, name, total in stats
      ]

# USERS WITH 0 POSTS -->
async def users_with_zero_posts(db : AsyncSession):
      result = await db.execute(
            select(User.id,User.name)
            .outerjoin(Post)
            .group_by(User.id,User.name)
            .having(func.count(Post.id) == 0)
            .order_by(User.id)
      )
      users = result.all()

      return [
            {
                  "id" : id,
                  "name" : name
            }
            for id , name in users
      ]

# POST SUMMARY -->
async def post_summary(db : AsyncSession):
      result = await db.execute(
            select(Post)
      )
      posts = result.scalars().all()

      return posts

# TOTAL POSTS -->
async def total_posts(db : AsyncSession):
      result = await db.execute(
            select(func.count()).select_from(Post)
      )
      total = result.scalar_one()

      return {
            "total_posts" : total
      }

# TOTAL POSTS BY SPECIFIC ID -->
async def total_posts_by_id(db : AsyncSession, user_id : int):
      result = await db.execute(
            select(Post)
            .where(Post.user_id == user_id)
      )
      total = result.scalars().all()

      return [
            {
                  "user_id" : user_id,
                  "total_posts" : total
            }
      ]