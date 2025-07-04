from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class ClubAdmin(Base):
    __tablename__ = "club_admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)

    user = relationship("User")
    club = relationship("Club")

    __table_args__ = (UniqueConstraint("user_id", "club_id", name="_user_club_uc"),)

    def __repr__(self):
        return f"<ClubAdmin(user_id={self.user_id}, club_id={self.club_id})>"
