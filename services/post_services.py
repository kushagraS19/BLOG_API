from sqlalchemy.orm import Session, joinedload
from schema.postDTO import Create_post, PostListResponse, PostWithUserResponse
from database.models import Post
from database.models import User
from sqlalchemy import asc, desc, or_ , func

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