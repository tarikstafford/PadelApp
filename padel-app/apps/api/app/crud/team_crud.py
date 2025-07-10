from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.models.team_membership import TeamMembershipRole, TeamMembershipStatus


class TeamCRUD:
    def get_team(self, db: Session, team_id: int) -> Optional[models.Team]:
        return (
            db.query(models.Team)
            .options(
                joinedload(models.Team.team_memberships).joinedload(models.TeamMembership.user),
                joinedload(models.Team.creator),
                joinedload(models.Team.stats),
            )
            .filter(models.Team.id == team_id)
            .first()
        )

    def get_teams_by_name(self, db: Session, name: str) -> list[models.Team]:
        return db.query(models.Team).filter(models.Team.name == name).all()

    def create_team(
        self, db: Session, team_data: schemas.TeamCreate, creator_id: int
    ) -> models.Team:
        # Get the creator user
        creator = db.query(models.User).filter(models.User.id == creator_id).first()
        if not creator:
            raise ValueError("Creator user not found")

        # Create team with new fields
        db_team = models.Team(
            name=team_data.name,
            description=team_data.description,
            logo_url=team_data.logo_url,
            created_by=creator_id,
            created_at=datetime.now(timezone.utc),
            is_active=team_data.is_active,
            players=[creator],  # Keep backward compatibility with old relationship
        )
        db.add(db_team)
        db.commit()
        db.refresh(db_team)

        # Create team membership for creator
        team_membership = models.TeamMembership(
            team_id=db_team.id,
            user_id=creator_id,
            role=TeamMembershipRole.OWNER,
            status=TeamMembershipStatus.ACTIVE,
            joined_at=datetime.now(timezone.utc),
        )
        db.add(team_membership)
        db.commit()
        db.refresh(team_membership)

        # Create team stats
        team_stats = models.TeamStats(team_id=db_team.id)
        db.add(team_stats)
        db.commit()

        return db_team

    def create_team_with_players(
        self, db: Session, name: str, players: list[models.User]
    ) -> models.Team:
        db_team = models.Team(name=name, players=players)
        db.add(db_team)
        db.commit()
        db.refresh(db_team)
        return db_team

    def add_player_to_team(
        self, db: Session, team: models.Team, user: models.User
    ) -> models.Team:
        team.players.append(user)
        db.add(team)
        db.commit()
        db.refresh(team)
        return team

    def get_user_teams(self, db: Session, user_id: int) -> list[models.Team]:
        """Get all teams that a user is a member of"""
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return []
        return user.teams

    def update_team(
        self, db: Session, team_id: int, team_data: schemas.TeamUpdate
    ) -> Optional[models.Team]:
        """Update team details"""
        team = db.query(models.Team).filter(models.Team.id == team_id).first()
        if not team:
            return None

        update_data = team_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(team, field, value)

        db.commit()
        db.refresh(team)
        return team

    # Team Membership CRUD Functions
    def add_team_member(
        self, db: Session, team_id: int, user_id: int, role: TeamMembershipRole = TeamMembershipRole.MEMBER
    ) -> Optional[models.TeamMembership]:
        """Add a member to a team"""
        # Check if user is already a member
        existing_membership = (
            db.query(models.TeamMembership)
            .filter(
                models.TeamMembership.team_id == team_id,
                models.TeamMembership.user_id == user_id,
                models.TeamMembership.is_active == True,
            )
            .first()
        )

        if existing_membership:
            return None  # User is already a member

        # Create new membership
        membership = models.TeamMembership(
            team_id=team_id,
            user_id=user_id,
            role=role,
            status=TeamMembershipStatus.ACTIVE,
            joined_at=datetime.now(timezone.utc),
        )
        db.add(membership)

        # Also add to the old players relationship for backward compatibility
        team = db.query(models.Team).filter(models.Team.id == team_id).first()
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if team and user and user not in team.players:
            team.players.append(user)

        db.commit()
        db.refresh(membership)
        return membership

    def remove_team_member(
        self, db: Session, team_id: int, user_id: int
    ) -> bool:
        """Remove a member from a team"""
        membership = (
            db.query(models.TeamMembership)
            .filter(
                models.TeamMembership.team_id == team_id,
                models.TeamMembership.user_id == user_id,
                models.TeamMembership.is_active == True,
            )
            .first()
        )

        if not membership:
            return False

        # Mark membership as inactive
        membership.status = TeamMembershipStatus.REMOVED
        membership.is_active = False
        membership.left_at = datetime.now(timezone.utc)

        # Also remove from old players relationship
        team = db.query(models.Team).filter(models.Team.id == team_id).first()
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if team and user and user in team.players:
            team.players.remove(user)

        db.commit()
        return True

    def update_team_member_role(
        self, db: Session, team_id: int, user_id: int, new_role: TeamMembershipRole
    ) -> Optional[models.TeamMembership]:
        """Update a team member's role"""
        membership = (
            db.query(models.TeamMembership)
            .filter(
                models.TeamMembership.team_id == team_id,
                models.TeamMembership.user_id == user_id,
                models.TeamMembership.is_active == True,
            )
            .first()
        )

        if not membership:
            return None

        membership.role = new_role
        db.commit()
        db.refresh(membership)
        return membership

    def get_team_members(
        self, db: Session, team_id: int
    ) -> list[models.TeamMembership]:
        """Get all active members of a team"""
        return (
            db.query(models.TeamMembership)
            .options(joinedload(models.TeamMembership.user))
            .filter(
                models.TeamMembership.team_id == team_id,
                models.TeamMembership.is_active == True,
                models.TeamMembership.status == TeamMembershipStatus.ACTIVE,
            )
            .order_by(models.TeamMembership.joined_at)
            .all()
        )

    def get_team_history(
        self, db: Session, team_id: int, limit: int = 20
    ) -> list[models.TeamGameHistory]:
        """Get team's game history"""
        return (
            db.query(models.TeamGameHistory)
            .filter(models.TeamGameHistory.team_id == team_id)
            .order_by(models.TeamGameHistory.game_date.desc())
            .limit(limit)
            .all()
        )

    def get_team_stats(
        self, db: Session, team_id: int
    ) -> Optional[models.TeamStats]:
        """Get team statistics"""
        return (
            db.query(models.TeamStats)
            .filter(models.TeamStats.team_id == team_id)
            .first()
        )

    def is_team_member(
        self, db: Session, team_id: int, user_id: int
    ) -> bool:
        """Check if user is an active member of the team"""
        membership = (
            db.query(models.TeamMembership)
            .filter(
                models.TeamMembership.team_id == team_id,
                models.TeamMembership.user_id == user_id,
                models.TeamMembership.is_active == True,
                models.TeamMembership.status == TeamMembershipStatus.ACTIVE,
            )
            .first()
        )
        return membership is not None

    def is_team_admin(
        self, db: Session, team_id: int, user_id: int
    ) -> bool:
        """Check if user is an admin or owner of the team"""
        membership = (
            db.query(models.TeamMembership)
            .filter(
                models.TeamMembership.team_id == team_id,
                models.TeamMembership.user_id == user_id,
                models.TeamMembership.is_active == True,
                models.TeamMembership.status == TeamMembershipStatus.ACTIVE,
            )
            .first()
        )
        return membership and membership.role in [TeamMembershipRole.ADMIN, TeamMembershipRole.OWNER]

    def get_user_team_memberships(
        self, db: Session, user_id: int
    ) -> list[models.TeamMembership]:
        """Get all active team memberships for a user"""
        return (
            db.query(models.TeamMembership)
            .options(joinedload(models.TeamMembership.team))
            .filter(
                models.TeamMembership.user_id == user_id,
                models.TeamMembership.is_active == True,
                models.TeamMembership.status == TeamMembershipStatus.ACTIVE,
            )
            .order_by(models.TeamMembership.joined_at)
            .all()
        )


team_crud = TeamCRUD()
