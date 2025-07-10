import enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy import Enum as SAEnum
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.database import Base


class TeamMembershipRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class TeamMembershipStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    REMOVED = "REMOVED"


class TeamMembership(Base):
    __tablename__ = "team_memberships"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(
        SAEnum(TeamMembershipRole, name="teammembershiprole"),
        nullable=False,
        default=TeamMembershipRole.MEMBER,
        server_default=TeamMembershipRole.MEMBER.value,
    )
    status = Column(
        SAEnum(TeamMembershipStatus, name="teammembershipstatus"),
        nullable=False,
        default=TeamMembershipStatus.ACTIVE,
        server_default=TeamMembershipStatus.ACTIVE.value,
    )
    joined_at = Column(DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))
    left_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, server_default="true")

    # Relationships
    team = relationship("Team", back_populates="team_memberships")
    user = relationship("User", back_populates="team_memberships")

    def __repr__(self):
        return (
            f"<TeamMembership(id={self.id}, team_id={self.team_id}, "
            f"user_id={self.user_id}, role='{self.role.value}', "
            f"status='{self.status.value}')>"
        )