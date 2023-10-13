from sqlalchemy.orm import Session
from sqlalchemy import select

from app import model as m
from app.logger import log

REGIONS = [
    {"en": "Haifa", "hebrew": "חיפה"},
    {"en": "Jerusalem", "hebrew": "ירושלים"},
    {"en": "North", "hebrew": "צָפוֹן"},
    {"en": "Center", "hebrew": "מֶרְכָּז"},
    {"en": "South", "hebrew": "דָרוֹם"},
    {"en": "Tel Aviv", "hebrew": "תל אביב"},
    {"en": "Judea", "hebrew": "יהודה"},
]


def create_locations(db: Session):
    """Create locations"""
    for name in REGIONS:
        location = db.scalar(select(m.Location).where(m.Location.name_en == name["en"]))
        if not location:
            location = m.Location(
                name_en=name["en"],
                name_hebrew=name["hebrew"],
            )
            db.add(location)
    db.commit()
    log(log.INFO, "Locations [%d] were created", len(REGIONS))
