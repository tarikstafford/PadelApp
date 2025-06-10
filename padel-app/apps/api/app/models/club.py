from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(String, nullable=True) # Address can be optional or have more structured fields later
    city = Column(String, index=True, nullable=True)
    postal_code = Column(String, index=True, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, index=True, nullable=True) # Should be unique if used for login/contact
    description = Column(Text, nullable=True)
    opening_hours = Column(Text, nullable=True) # e.g., "Mon-Fri: 9am-10pm, Sat-Sun: 8am-11pm" or JSON string
    amenities = Column(Text, nullable=True) # e.g., "parking,showers,pro-shop"
    image_url = Column(String, nullable=True)

    # New fields for ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="owned_club")

    # Relationship to Court model
    courts = relationship("Court", back_populates="club", cascade="all, delete-orphan")

    # Relationship to ClubAdmin model
    admins = relationship("ClubAdmin", back_populates="club", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Club(id={self.id}, name='{self.name}')>" 