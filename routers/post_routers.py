from fastapi import APIRouter, Depends, HTTPException, Query
from schema.postDTO import Create_post, Post_update, PostResponse, PostListResponse, PostWithUserResponse, PostPerUser, PostSummaryResponse
from database.database import get_db
from database.models import Post, User
from sqlalchemy.orm import Session, joinedload, load_only
from dependencies.auth import get_current_user
from dependencies.permissions import admin_required
from typing import Optional, Literal
from sqlalchemy import asc, desc, or_ , func
import services.post_services as post_services

post_router = APIRouter(
    prefix = "/posts",
    tags = ["Posts"]
)

# CREATE A POST -->
@post_router.post("/create_post", status_code = 201, response_model = PostResponse )
def create_post(payload : Create_post, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return post_services.create_post(
        db,
        payload,
        current_user
    )

# GET ALL POSTS -->
@post_router.get("/all_posts", response_model = PostListResponse)
def get_all_posts(
    title : Optional[str] = None,
    user_id : Optional[int] = None,
    sort_by : Literal[
        "id",
        "title",
        "user_id",
        "description"
    ] = "id",
    order : Literal[
        "asc",
        "desc"
    ] = "asc",
    limit : int = Query(10, ge = 1 , le = 100),
    offset : int = Query(0, ge = 0),
    db : Session = Depends(get_db), 
    search : Optional[str] = None,
    ):

    return post_services.get_all_posts(
        db = db,
        title = title,
        user_id = user_id,
        search = search,
        sort_by = sort_by,
        order = order,
        limit = limit,
        offset = offset
    )

# GET POST WITH USER NAME AND EMAIL
@post_router.get("/posts/with-user", response_model = list[PostWithUserResponse])
def get_post_with_user(db : Session = Depends(get_db)):

    return post_services.get_post_with_user(db = db)

# TOTAL POSTS -->
@post_router.get("/posts/stats/total")
def give_total_posts(db : Session = Depends(get_db)):
    total = db.query(func.count(Post.id)).scalar()

    return {
        "total_posts" : total
    }

# TOTAL POSTS BY SPECIFIC ID -->
@post_router.get("/posts/stats/total/{user_id}")
def give_total_posts_by_user_id(user_id : int, db : Session = Depends(get_db)):
    total = (
        db.query(func.count(Post.id)).filter(Post.user_id == user_id).scalar()
    )

    return {
        "user_id" : user_id,
        "total_posts" : total
    }

# POSTS PER USER -->
@post_router.get("/posts/stats/user-posts", response_model = list[PostPerUser])
def post_per_user(db : Session = Depends(get_db)):
    return post_services.posts_per_user(db = db)

# USERS WHO HAVE ATLEAST 2 POSTS WITH PYTHON IN ITS TITLE -->
@post_router.get("/posts/stats/active-users")
def active_users(db : Session = Depends(get_db)):

    return post_services.active_users(db = db)

# GET POST BY ID -->
@post_router.get("/posts/{post_id}")
def get_post_by_id(post_id : int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return post_services.get_post_by_id(
        db = db,
        post_id = post_id
    )

# DELETE A POST --> 
@post_router.delete("/deletepost/{post_id}")
def delete_post(post_id : int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code = 404,
            detail = "Post not found"
        )

    if post.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code = 403,
            detail = "Unauthorized"
        )
    
    db.delete(post)
    db.commit()

    return {
        "message" : "Post deleted successfully"
    }

# UPDATE A POST -->
@post_router.put("/update_post/{post_id}", response_model = PostResponse)
def update_post(post_id : int,payload : Post_update, db : Session = Depends(get_db), current_user = Depends(get_current_user)):

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code = 404,
            detail = "Post not found"
        )
    
    if post.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code = 403,
            detail = "Unauthorized"
        )

    updates = payload.model_dump(exclude_unset = True)

    for key, value in updates.items():
        setattr(post, key, value)

    db.commit()     
    db.refresh(post)    

    return post

# All-users Stats -->
@post_router.get("/posts/stats/all-users")
def all_users_stats(db : Session = Depends(get_db)):
    result = (
        db.query(
            User.id,
            User.name,
            func.count(Post.id).label("total_posts")
        ).outerjoin(Post)
            .group_by(User.id, User.name)
            .order_by(User.id)
            .all()
    )
    return [
        {
            "user_id" : user_id,
            "name" : name,
            "total_posts" : total
        }
        for user_id, name, total in result
    ]

# USERS WITH 0 POSTS -->
@post_router.get("/posts/stats/all_with_zero_posts")
def users_with_zero_posts(db : Session = Depends(get_db)):
    result = (
        db.query(
            User.id,
            User.name
        ).outerjoin(Post).group_by(User.id, User.name).having(func.count(Post.id) == 0).order_by(User.id).all()
    )
    
    return [
        {
            "user_id" : id,
            "name" : name
        }
        for id, name in result
    ]

# GET POST SUMMARY -->
@post_router.get("/summary", response_model = list[PostSummaryResponse])
def post_summary(db : Session = Depends(get_db)):
    print("endpoint reached mutherfucker..")
    posts = db.query(Post).all()

    return posts