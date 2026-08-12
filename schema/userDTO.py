from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schema.postDTO import PostResponse

class Create_user(BaseModel):
    id : Optional[int]
    name : str
    email : str
    password : str
    role : str

class User_response(BaseModel):
    id : int
    name : str
    email : str

    model_config = ConfigDict(from_attributes = True)

class UserResponseList(BaseModel):
    total_users : int
    users : list[User_response]

class AdminDashboardResponse(BaseModel):
    id : int
    name : str
    posts : list[PostResponse]

    model_config = ConfigDict(from_attributes = True)

class User_profile(BaseModel):
    id : int
    name : str
    email : str
    posts : list[PostResponse]