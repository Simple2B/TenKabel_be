from sqlalchemy import select
from sqlalchemy.orm import Session
from invoke import task
from app.config import Settings, get_settings
from app.model import User, Profession, Location, Job
from app.logger import log

settings: Settings = get_settings()

NUM_TEST_USERS = 1000
NUM_TEST_JOBS = 27


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

LOCATIONS = [
    {"en": "Afula", "hebrew": "עפולה"},
    {"en": "Akko", "hebrew": "עכו"},
    {"en": "Arad", "hebrew": "ערד"},
    {"en": "Ariel", "hebrew": "אריאל"},
    {"en": "Ashdod", "hebrew": "אשדוד"},
    {"en": "Ashkelon", "hebrew": "אשקלון"},
    {"en": "Baqa al-Gharbiyye", "hebrew": "בקעה על גרבייה"},
    {"en": "Bat Yam", "hebrew": "בת ים"},
    {"en": "Beer Sheva", "hebrew": "באר שבע"},
    {"en": "Beit Shean", "hebrew": "בית שאן"},
    {"en": "Beit Shemesh", "hebrew": "בית שמש"},
    {"en": "Betar Illit", "hebrew": "ביתר עילית"},
    {"en": "Bnei Berak", "hebrew": "בני ברק"},
    {"en": "Dimona", "hebrew": "דימונה"},
    {"en": "Eilat", "hebrew": "אילת"},
    {"en": "Elad", "hebrew": "אלעד"},
    {"en": "Givatayim", "hebrew": "	גבעתיים"},
    {"en": "Hadera", "hebrew": "חדרה"},
    {"en": "Haifa", "hebrew": "חיפה"},
    {"en": "Harish", "hebrew": "חריש"},
    {"en": "Herzliya", "hebrew": "הרצליה"},
    {"en": "Hod HaSharon", "hebrew": "הוד השרון"},
    {"en": "Holon", "hebrew": "חולון"},
    {"en": "Jerusalem", "hebrew": "ירושלים"},
    {"en": "Karmiel", "hebrew": "כרמיאל"},
    {"en": "Kfar Sava", "hebrew": "כפר סבא"},
    {"en": "Kiryat Ata", "hebrew": "קרית אתא"},
    {"en": "Kiryat Bialik", "hebrew": "קרית ביאליק"},
    {"en": "Kiryat Gat", "hebrew": "קרית גת"},
    {"en": "Kiryat Malachi", "hebrew": "קרית מלאכי"},
    {"en": "Kiryat Motzkin", "hebrew": "קרית מוצקין"},
    {"en": "Kiryat Ono", "hebrew": "קרית אונו"},
    {"en": "Kiryat Shemone", "hebrew": "קרית שמונה"},
    {"en": "Kiryat Yam", "hebrew": "קרית ים"},
    {"en": "Lod", "hebrew": "לוד"},
    {"en": "Maale Adumim", "hebrew": "מעלה אדומים"},
    {"en": "Maalot Tarshiha", "hebrew": "מעלות-תרשיחא"},
    {"en": "Migdal HaEmek", "hebrew": "מגדל העמק"},
    {"en": "Modiin", "hebrew": "מודיעין-מכבים-רעות"},
    {"en": "Nahariya", "hebrew": "נהריה"},
    {"en": "Nazareth", "hebrew": "נצרת"},
    {"en": "Nes Ziona", "hebrew": "נס ציונה"},
    {"en": "Nesher", "hebrew": "נשר"},
    {"en": "Netanya", "hebrew": "נתניה"},
    {"en": "Netivot", "hebrew": "נתיבות"},
    {"en": "Nof Hagalil", "hebrew": "נוף הגליל"},
    {"en": "Ofakim", "hebrew": "אופקים"},
    {"en": "Or Akiva", "hebrew": "אור עקיבא"},
    {"en": "Or Yehuda", "hebrew": "אור יהודה"},
    {"en": "Petah Tikva", "hebrew": "פתח תקוה"},
    {"en": "Qalansawe", "hebrew": "קלנסווה"},
    {"en": "Raanana", "hebrew": "רעננה"},
    {"en": "Rahat", "hebrew": "רהט"},
    {"en": "Ramat Hasharon", "hebrew": "רמת השרון"},
    {"en": "Ramat-Gan", "hebrew": "רמת גן"},
    {"en": "Ramla", "hebrew": "רמלה"},
    {"en": "Rehovot", "hebrew": "רחובות"},
    {"en": "Rishon Lezion", "hebrew": "ראשון לציון"},
    {"en": "Rosh Ha'ayin", "hebrew": "ראש העין"},
    {"en": "Sakhnin", "hebrew": "סח'נין"},
    {"en": "Sderot", "hebrew": "שדרות"},
    {"en": "Shefaram", "hebrew": "שפרעם"},
    {"en": "Taibeh", "hebrew": "טייבה"},
    {"en": "Tamra", "hebrew": "תמרה"},
    {"en": "Tel Aviv", "hebrew": "תל אביב-יפו"},
    {"en": "Tiberias", "hebrew": "טבריה"},
    {"en": "Tira", "hebrew": "טירה"},
    {"en": "Tirat Carmel", "hebrew": "טירת כרמל"},
    {"en": "Tsfat (Safed)", "hebrew": "צפת"},
    {"en": "Umm al-Fahm", "hebrew": "אום אל-פחם"},
    {"en": "Yavne", "hebrew": "יבנה"},
    {"en": "Yehud-Monosson", "hebrew": "יהוד-מונוסון"},
    {"en": "Yokneam", "hebrew": "יקנעם"},
]


@task
def init_db(_, test_data=False):
    """Initialization database

    Args:
        --test-data (bool, optional): wether fill database by test data. Defaults to False.
    """
    from app.database import db as dbo

    db = dbo.Session()
    create_professions(db)
    create_locations(db)
    # add admin user
    admin = User(
        username=settings.ADMIN_USER,
        password=settings.ADMIN_PASS,
        email=settings.ADMIN_EMAIL,
        phone="972 54 000 00000",
        is_verified=True,
    )
    db.add(admin)
    if test_data:
        # Add test data
        fill_test_data(db)

    db.commit()


def fill_test_data(db: Session):
    for uid in range(NUM_TEST_USERS):
        user = User(
            username=f"User{uid}",
            first_name=f"Jack{uid}",
            last_name=f"London{uid}",
            email=f"user{uid}@test.com",
            phone=f"972 54 000 {uid+1:04}",
            is_verified=True,
        )
        db.add(user)


def create_professions(db: Session):
    for name in PROFESSIONS:
        db.add(
            Profession(
                name_en=name["en"],
                name_hebrew=name["hebrew"],
            )
        )

    db.commit()
    log(log.INFO, "Professions [%d] were created", len(PROFESSIONS))


def create_locations(db: Session):
    """Create locations"""
    for name in LOCATIONS:
        location = Location(
            name_en=name["en"],
            name_hebrew=name["hebrew"],
        )
        db.add(location)

    db.commit()
    log(log.INFO, "Locations [%d] were created", len(LOCATIONS))


# TODO:
@task
def create_jobs(_):
    """Create test jobs"""
    from app.database import db as dbo

    db = dbo.Session()
    owners = db.scalars(select(User).order_by(User.id)).all()
    log(log.INFO, "Owners [%d] ", len(owners))
    professions = db.scalars(select(Profession).order_by(Profession.id)).all()
    log(log.INFO, "Professions [%d] ", len(professions))
    for uid in range(NUM_TEST_JOBS):
        job = Job(
            owner_id=owners[uid].id,
            profession_id=professions[uid].id,
            name="name",
            description="description",
        )
        db.add(job)
    db.commit()
    log(log.INFO, "Jobs [%d] created", NUM_TEST_JOBS)
