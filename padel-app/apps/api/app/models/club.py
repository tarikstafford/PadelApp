from datetime import time

from sqlalchemy import Column, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import relationship

from app.database import Base


class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(
        String, nullable=True
    )  # Address can be optional or have more structured fields later
    city = Column(String, index=True, nullable=True)
    postal_code = Column(String, index=True, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(
        String, index=True, nullable=True
    )  # Should be unique if used for login/contact
    description = Column(Text, nullable=True)

    # Structured time fields for programmatic use
    opening_time = Column(Time, default=time(9, 0))  # Default 9:00 AM
    closing_time = Column(Time, default=time(22, 0))  # Default 10:00 PM

    amenities = Column(Text, nullable=True)  # e.g., "parking,showers,pro-shop"
    image_url = Column(String, nullable=True)

    # New fields for ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="owned_club")

    # Relationship to Court model
    courts = relationship("Court", back_populates="club", cascade="all, delete-orphan")

    # Relationship to ClubAdmin model
    admins = relationship(
        "ClubAdmin", back_populates="club", cascade="all, delete-orphan"
    )
    
    # Financial and analytics relationships
    payment_transactions = relationship(
        "PaymentTransaction", back_populates="club", cascade="all, delete-orphan"
    )
    revenue_records = relationship(
        "RevenueRecord", back_populates="club", cascade="all, delete-orphan"
    )
    daily_analytics = relationship(
        "ClubDailyAnalytics", back_populates="club", cascade="all, delete-orphan"
    )
    memberships = relationship(
        "ClubMembership", back_populates="club", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Club(id={self.id}, name='{self.name}')>"
