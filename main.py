from fastapi import FastAPI
from app.routers.user_routes import user_router
from app.routers.auth_routes import auth_router
from app.routers.post_routers import post_router

app = FastAPI()


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(post_router)

# MAKE A ROUTE FOR UPDATE POST ******