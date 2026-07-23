from fastapi import FastAPI
from database.database import Base, engine
from routers.user_routes import user_router
from routers.auth_routes import auth_router
from routers.post_routers import post_router

app = FastAPI()

Base.metadata.create_all(bind = engine)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(post_router)

# MAKE A ROUTE FOR UPDATE POST ******