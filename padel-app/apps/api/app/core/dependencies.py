from fastapi import Depends, HTTPException, status, Path
from typing import List
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.models import User, UserRole
from app.crud import club_admin_crud, booking_crud
from app.database import get_db

def RoleChecker(allowed_roles: List[UserRole]):
    def _check_role(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with role {current_user.role} is not permitted to access this resource.",
            )
        return current_user
    return _check_role 

def ClubAdminChecker():
    def _check_club_admin(
        club_id: int = Path(..., title="The ID of the club to check"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user

        is_admin = club_admin_crud.get_club_admin(db, user_id=current_user.id, club_id=club_id)
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have administrative access to this club.",
            )
        return current_user
    return _check_club_admin 

def BookingAdminChecker():
    def _check_booking_admin(
        booking_id: int = Path(..., title="The ID of the booking to check"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        booking = booking_crud.get_booking(db, booking_id=booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        
        club_id = booking.court.club_id
        
        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user

        is_admin = club_admin_crud.get_club_admin(db, user_id=current_user.id, club_id=club_id)
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have administrative access to this club.",
            )
        return current_user
    return _check_booking_admin 