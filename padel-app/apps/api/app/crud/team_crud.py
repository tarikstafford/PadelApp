from typing import List, Optional
from sqlalchemy.orm import Session
from app import models, schemas

def get_team(db: Session, team_id: int) -> Optional[models.Team]:
    return db.query(models.Team).filter(models.Team.id == team_id).first()

def get_teams_by_name(db: Session, name: str) -> List[models.Team]:
    return db.query(models.Team).filter(models.Team.name == name).all()

def create_team(db: Session, team: schemas.TeamCreate) -> models.Team:
    db_team = models.Team(name=team.name)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def create_team_with_players(db: Session, name: str, players: List[models.User]) -> models.Team:
    db_team = models.Team(name=name, players=players)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def add_player_to_team(db: Session, team: models.Team, user: models.User) -> models.Team:
    team.players.append(user)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team 