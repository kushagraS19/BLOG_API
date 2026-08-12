from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.main import app

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