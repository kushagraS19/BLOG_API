from pydantic import BaseModel, ConfigDict
from typing import Optional

class Create_post(BaseModel):
    id : Optional[int]
    title : str
    description : str

class Post_update(BaseModel):
    title : Optional[str]
    description : Optional[str]

class PostResponse(BaseModel):
    id : int
    title : str
    description : str

    model_config = ConfigDict(from_attributes = True)

class PostListResponse(BaseModel):
    total_posts : int
    limit : int
    offset : int
    posts : list[PostResponse]

class PostWithUserResponse(BaseModel):
    id : int
    title : str
    description : str
    author : str
    author_email : str

class PostPerUser(BaseModel):
    name : str
    total_posts : int

