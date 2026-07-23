from pydantic import BaseModel, ConfigDict
from typing import Optional
from schema.postDTO import PostResponse

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

class AdminDashboardResponse(BaseModel):
    id : int
    name : str
    posts : list[PostResponse]

    model_config = ConfigDict(from_attributes = True)