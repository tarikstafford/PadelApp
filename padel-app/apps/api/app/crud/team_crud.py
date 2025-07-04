from typing import Optional

from sqlalchemy.orm import Session

from app import models, schemas


class TeamCRUD:
    def get_team(self, db: Session, team_id: int) -> Optional[models.Team]:
        return db.query(models.Team).filter(models.Team.id == team_id).first()

    def get_teams_by_name(self, db: Session, name: str) -> list[models.Team]:
        return db.query(models.Team).filter(models.Team.name == name).all()

    def create_team(
        self, db: Session, team_data: schemas.TeamCreate, creator_id: int
    ) -> models.Team:
        # Get the creator user
        creator = db.query(models.User).filter(models.User.id == creator_id).first()
        if not creator:
            raise ValueError("Creator user not found")

        # Create team with creator as first player
        db_team = models.Team(name=team_data.name, players=[creator])
        db.add(db_team)
        db.commit()
        db.refresh(db_team)
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


team_crud = TeamCRUD()
