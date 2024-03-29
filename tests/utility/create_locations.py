from sqlalchemy.orm import Session
from sqlalchemy import select

from app import model as m
from app.logger import log

REGIONS = [
    {"en": "Haifa", "hebrew": "חיפה"},
    {"en": "Jerusalem", "hebrew": "ירושלים"},
    {"en": "North", "hebrew": "צפון"},
    {"en": "Center", "hebrew": "מרכז"},
    {"en": "South", "hebrew": "דרום"},
    {"en": "Tel Aviv", "hebrew": "תל אביב"},
    {"en": "Ye”sh", "hebrew": "יו”ש"},
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
