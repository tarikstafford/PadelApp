from decimal import Decimal  # For price_per_hour

from sqlalchemy.orm import Session

from app.models import Club, Court


def seed_clubs(db: Session) -> None:
    clubs_data = [
        {
            "name": "City Padel Center",
            "address": "123 Urban Ave",
            "city": "Metroville",
            "postal_code": "MV123",
            "phone": "555-0101",
            "email": "info@citypadel.com",
            "description": "Premier downtown Padel destination.",
            "opening_hours": "Mon-Sun: 7am-11pm",
            "amenities": "Cafe, Pro Shop, Lockers, Showers, Parking",
            "image_url": "https://via.placeholder.com/400x250?text=City+Padel+Center",
        },
        {
            "name": "Suburban Racquet Club",
            "address": "456 Green Park Rd",
            "city": "Suburbia",
            "postal_code": "SB456",
            "phone": "555-0102",
            "email": "contact@suburbanracquet.com",
            "description": "Family-friendly club with excellent facilities.",
            "opening_hours": "Mon-Fri: 8am-10pm, Sat-Sun: 8am-8pm",
            "amenities": "Parking, Kids Area, Coaching",
            "image_url": "https://via.placeholder.com/400x250?text=Suburban+Racquet",
        },
        {
            "name": "Coastal Padel Courts",
            "address": "789 Ocean View Dr",
            "city": "Beachtown",
            "postal_code": "BT789",
            "phone": "555-0103",
            "email": "play@coastalpadel.com",
            "description": "Play with a view of the ocean.",
            "opening_hours": "Mon-Sun: 9am-9pm",
            "amenities": "Sea Breeze, Outdoor Courts, Snack Bar",
            "image_url": "https://via.placeholder.com/400x250?text=Coastal+Padel",
        },
        {
            "name": "Highland Padel Club",
            "address": "101 Mountain Pass",
            "city": "Hilltop",
            "postal_code": "HT101",
            "phone": "555-0104",
            "email": "manager@highlandpadel.com",
            "description": "Exclusive club with panoramic views.",
            "opening_hours": "Mon-Sat: 10am-7pm",
            "amenities": "Heated Courts, Lounge, Private Lessons",
            "image_url": "https://via.placeholder.com/400x250?text=Highland+Padel",
        },
        {
            "name": "Industrial Padel Zone",
            "address": "202 Factory Ln",
            "city": "Industry City",
            "postal_code": "IC202",
            "phone": "555-0105",
            "email": "bookings@industrialpadel.com",
            "description": "Converted warehouse space, unique atmosphere.",
            "opening_hours": "24/7 Access for Members",
            "amenities": "Automated Booking, High Ceilings, Robust Courts",
            "image_url": "https://via.placeholder.com/400x250?text=Industrial+Padel",
        },
    ]

    for club_info in clubs_data:
        db_club = db.query(Club).filter(Club.name == club_info["name"]).first()
        if not db_club:
            new_club = Club(**club_info)
            db.add(new_club)
            print(f"Club '{new_club.name}' seeded.")
        else:
            print(f"Club '{club_info['name']}' already exists, skipping.")
    db.commit()


def seed_courts(db: Session) -> None:
    courts_data = [
        # City Padel Center
        {
            "club_name": "City Padel Center",
            "name": "Court A1",
            "surface_type": "Artificial Grass Pro",
            "is_indoor": True,
            "price_per_hour": Decimal("30.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "City Padel Center",
            "name": "Court A2",
            "surface_type": "Artificial Grass Pro",
            "is_indoor": True,
            "price_per_hour": Decimal("30.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "City Padel Center",
            "name": "Court B1 (Glass)",
            "surface_type": "Panoramic Glass",
            "is_indoor": True,
            "price_per_hour": Decimal("35.00"),
            "default_availability_status": "Maintenance",
        },
        {
            "club_name": "City Padel Center",
            "name": "Court C1 (Outdoor)",
            "surface_type": "ConcreteTextured",
            "is_indoor": False,
            "price_per_hour": Decimal("25.00"),
            "default_availability_status": "Available",
        },
        # Suburban Racquet Club
        {
            "club_name": "Suburban Racquet Club",
            "name": "Family Court 1",
            "surface_type": "Cushioned Hard Court",
            "is_indoor": True,
            "price_per_hour": Decimal("28.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "Suburban Racquet Club",
            "name": "Family Court 2",
            "surface_type": "Cushioned Hard Court",
            "is_indoor": True,
            "price_per_hour": Decimal("28.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "Suburban Racquet Club",
            "name": "Training Court",
            "surface_type": "Artificial Grass",
            "is_indoor": False,
            "price_per_hour": Decimal("22.00"),
            "default_availability_status": "Available",
        },
        # Coastal Padel Courts
        {
            "club_name": "Coastal Padel Courts",
            "name": "Ocean Breeze 1",
            "surface_type": "Sand-filled Synthetic",
            "is_indoor": False,
            "price_per_hour": Decimal("26.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "Coastal Padel Courts",
            "name": "Ocean Breeze 2",
            "surface_type": "Sand-filled Synthetic",
            "is_indoor": False,
            "price_per_hour": Decimal("26.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "Coastal Padel Courts",
            "name": "Sunset View Court",
            "surface_type": "Panoramic Glass",
            "is_indoor": False,
            "price_per_hour": Decimal("32.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "Coastal Padel Courts",
            "name": "Sheltered Court",
            "surface_type": "Artificial Grass",
            "is_indoor": True,
            "price_per_hour": Decimal("29.00"),
            "default_availability_status": "Available",
        },
        # Highland Padel Club
        {
            "club_name": "Highland Padel Club",
            "name": "Peak Court 1",
            "surface_type": "Premium Synthetic",
            "is_indoor": True,
            "price_per_hour": Decimal("40.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "Highland Padel Club",
            "name": "Peak Court 2",
            "surface_type": "Premium Synthetic",
            "is_indoor": True,
            "price_per_hour": Decimal("40.00"),
            "default_availability_status": "Maintenance",
        },
        {
            "club_name": "Highland Padel Club",
            "name": "Valley View Court",
            "surface_type": "Textured Concrete",
            "is_indoor": False,
            "price_per_hour": Decimal("35.00"),
            "default_availability_status": "Available",
        },
        # Industrial Padel Zone
        {
            "club_name": "Industrial Padel Zone",
            "name": "Zone Alpha",
            "surface_type": "Industrial Grade Turf",
            "is_indoor": True,
            "price_per_hour": Decimal("20.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "Industrial Padel Zone",
            "name": "Zone Beta",
            "surface_type": "Industrial Grade Turf",
            "is_indoor": True,
            "price_per_hour": Decimal("20.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "Industrial Padel Zone",
            "name": "Zone Gamma",
            "surface_type": "Polished Concrete",
            "is_indoor": True,
            "price_per_hour": Decimal("18.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "Industrial Padel Zone",
            "name": "Zone Delta (Outdoor)",
            "surface_type": "Asphalt",
            "is_indoor": False,
            "price_per_hour": Decimal("15.00"),
            "default_availability_status": "Available",
        },
        {
            "club_name": "Industrial Padel Zone",
            "name": "Zone Epsilon",
            "surface_type": "Industrial Grade Turf",
            "is_indoor": True,
            "price_per_hour": Decimal("20.00"),
            "default_availability_status": "Available",
        },
    ]

    for court_info in courts_data:
        club = db.query(Club).filter(Club.name == court_info["club_name"]).first()
        if club:
            db_court = (
                db.query(Court)
                .filter(Court.name == court_info["name"], Court.club_id == club.id)
                .first()
            )
            if not db_court:
                new_court = Court(
                    name=court_info["name"],
                    club_id=club.id,
                    surface_type=court_info["surface_type"],
                    is_indoor=court_info["is_indoor"],
                    price_per_hour=court_info["price_per_hour"],
                    default_availability_status=court_info[
                        "default_availability_status"
                    ],
                )
                db.add(new_court)
                print(f"Court '{new_court.name}' for club '{club.name}' seeded.")
            else:
                print(
                    f"Court '{court_info['name']}' for club '{club.name}' already exists, skipping."
                )
        else:
            print(
                f"Club '{court_info['club_name']}' not found for court '{court_info['name']}', skipping."
            )
    db.commit()


def seed_all_data(db: Session) -> None:
    print("Starting database seeding...")
    seed_clubs(db)
    seed_courts(db)
    print("Database seeding completed.")


# Example of how this might be run (will be called from run_seeds.py)
# if __name__ == "__main__":
#     from app.database import SessionLocal
#     db_session = SessionLocal()
#     try:
#         seed_all_data(db_session)
#     finally:
#         db_session.close()
