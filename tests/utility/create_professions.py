from sqlalchemy.orm import Session
from sqlalchemy import select

from app import model as m
from app.logger import log

PROFESSIONS = [
    {"en": "Plumber", "hebrew": "אינסטלטור"},
    {"en": "Electrician", "hebrew": "חשמלאי"},
    {"en": "Handyman", "hebrew": "הנדימן"},
    {"en": "Exterminator", "hebrew": "מדביר"},
    {"en": "Painter", "hebrew": "צבע"},
    {"en": "Ac technician", "hebrew": "מיזוג אוויר"},
    {"en": "Locksmith & Doors", "hebrew": "מנעולים ודלתות"},
    {"en": "Boilers", "hebrew": "דודי שמש"},
    {"en": "Movers", "hebrew": "הובלות"},
    {"en": "Gardner", "hebrew": "גינון"},
    {"en": "Cleaning & maintenance", "hebrew": "ניקיון ואחזקה"},
    {"en": "Glass and windows", "hebrew": "חלונות וזכוכית"},
    {"en": "Gas technicians", "hebrew": "טכנאי גז"},
    {"en": "Snake removal", "hebrew": "לכידת נחשים"},
    {"en": "Carpenter", "hebrew": "נגרות ומטבחים"},
    {"en": "Tow truck", "hebrew": "גרר"},
    {"en": "Carpet/sofa cleaning", "hebrew": "ניקיון ספות ושטיחים"},
    {"en": "Drywall", "hebrew": "גבס"},
    {"en": "Polish", "hebrew": "פוליש"},
    {"en": "Concrete saw", "hebrew": "ניסור בטון"},
    {"en": "Construction", "hebrew": "בניה"},
    {"en": "Construction inspection", "hebrew": "פיקוח בניה"},
    {"en": "Concrete truck", "hebrew": "משאית בטון"},
    {"en": "Tiles", "hebrew": "רצף"},
    {"en": "Low current", "hebrew": "מתח נמוך"},
    {"en": "Sprinklers", "hebrew": "ספרינקלרים"},
    {"en": "Rentals", "hebrew": "השכרות"},
]


def create_professions(db: Session):
    counter = 0
    for name in PROFESSIONS:
        profession = db.scalars(
            select(m.Profession).where(m.Profession.name_en == name["en"])
        ).first()
        if not profession:
            db.add(
                m.Profession(
                    name_en=name["en"],
                    name_hebrew=name["hebrew"],
                )
            )
            db.commit()
            counter += 1

    log(log.INFO, "Professions [%d] were created", counter)
