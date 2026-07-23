from fastapi import Depends, HTTPException
from dependencies.auth import get_current_user

def admin_required(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code = 403,
            detail = "Only admins can use this field"
        )
    
    return current_user