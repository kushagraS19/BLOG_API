from sqlalchemy.orm import Session, joinedload
from schema.postDTO import Create_post, PostListResponse, PostWithUserResponse, PostPerUser
from database.models import Post
from database.models import User
from sqlalchemy import asc, desc, or_ , func
from fastapi import HTTPException

# CREATE POST -->
def create_post(db : Session, payload : Create_post, current_user : User):

    post = Post(
        title = payload.title,
        description = payload.description,
        user_id = current_user.id
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

# GET ALL POSTS -->
def get_all_posts(
        db : Session,
        title : str | None,
        user_id : int | None,
        search : str | None,
        sort_by : str,
        order : str,
        limit : int,
        offset : int
):
    query = db.query(Post)
    
    if title:
            query = query.filter(Post.title.ilike(f"%{title}%"))
    
    if user_id:
            query = query.filter(Post.user_id == user_id)
    
    if search:
            query = query.filter(
                or_(
                    Post.title.ilike(f"%{search}%"),
                    Post.description.ilike(f"%{search}%")
                )
            )
    
    column = getattr(Post, sort_by)
    
    query = query.order_by(
            asc(column) if order == "asc" else desc(column)
        )
    
    query = query.offset(offset).limit(limit).all()
    total_posts = query.count()
    
    return PostListResponse(
            total_posts = total_posts,
            limit = limit,
            offset = offset,
            posts = query
        )

# GET POST WITH USER -->
def get_post_with_user(db : Session):
      posts = (
            db.query(Post).options(joinedload(Post.user)).all()
      )

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
def posts_per_user(db : Session):
      print("before")
      posts = (
            db.query(
                  User.name,
                  func.count(Post.id).label("total_posts"))
                  .outerjoin(Post)
                  .group_by(User.name)
                  .all()
      )
      print("after")

      return [
            PostPerUser(
            name = name,
            total_posts = total
      )
      for name, total in posts
      ]

# USERS WHO HAVE ATLEAST 2 POSTS WITH PYTHON IN ITS TITLE -->
def active_users(db : Session):
      users = (
            db.query(
                  User.name,
                  User.name,
                  func.count(Post.id).label("total_posts")
            ).join(User)
            .filter(Post.title.ilike("%Python%"))
            .group_by(User.id, User.name)
            .having(func.count(Post.id) >= 2)
            .order_by(User.id)
            .all()
      )

      return [
            {
                  "user_id" : id,
                  "user_name" : name,
                  "total_posts" : total
            }
            for id, name, total in users
      ]

# GET POST BY ID -->
def get_post_by_id(db : Session, post_id : int):
      post = db.query(Post).filter(Post.id == post_id).first()

      if not post:
            raise HTTPException(
                  status_code = 404,
                  detail = "Post not found"
            )

      return post

# DELETE A POST -->
def delete_post(db : Session, post_id : int, current_user : User):
      post = db.query(Post).filter(Post.id == post_id).first()

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

      db.delete(post)
      db.commit()