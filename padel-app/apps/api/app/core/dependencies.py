from fastapi import Depends, HTTPException, status
from typing import List

from app.core.security import get_current_active_user
from app.models import User, UserRole

def RoleChecker(allowed_roles: List[UserRole]):
    def _check_role(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with role {current_user.role} is not permitted to access this resource.",
            )
        return current_user
    return _check_role 