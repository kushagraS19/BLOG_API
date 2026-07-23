from database.database import Base
from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):

    __tablename__ = "users"
    
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(String)
    
    posts = relationship(
        "Post",
        back_populates = "user"
    )

class Post(Base):

    __tablename__ = "posts"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String)
    description = Column(String)
    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    user = relationship(
        "User",
        back_populates = "posts"
    )