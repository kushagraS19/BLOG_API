from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.main import app
from app.exceptions.custom import UserNotFoundError

@app.exception_handler(ValueError)
async def value_error_handler(
    request : Request,
    exc : ValueError
):
    return JSONResponse(
        status_code = 400,
        content = {
            "message" : str(exc)
        }
    )

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request : Request, exc : UserNotFoundError):
    return JSONResponse(
        status_code = 404,
        content = {
            "message" : str(exc)
        }
    )