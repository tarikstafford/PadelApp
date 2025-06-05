from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(String, nullable=True) # Address can be optional or have more structured fields later
    city = Column(String, nullable=True, index=True)
    postal_code = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    description = Column(Text, nullable=True)
    opening_hours = Column(Text, nullable=True) # e.g., "Mon-Fri: 9am-10pm, Sat-Sun: 8am-11pm" or JSON string
    amenities = Column(Text, nullable=True) # e.g., "Parking, Cafe, Showers" or JSON string of list
    image_url = Column(String, nullable=True)

    # Relationship to Court model
    courts = relationship("Court", back_populates="club", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Club(id={self.id}, name='{self.name}')>" 