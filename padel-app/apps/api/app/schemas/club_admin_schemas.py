from pydantic import BaseModel

# Shared properties
class ClubAdminBase(BaseModel):
    user_id: int
    club_id: int

# Properties to receive on creation
class ClubAdminCreate(ClubAdminBase):
    pass

# Properties to return to client
class ClubAdmin(ClubAdminBase):
    id: int

    class Config:
        orm_mode = True 