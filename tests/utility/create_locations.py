from sqlalchemy.orm import Session
from sqlalchemy import select

from app import model as m
from app.logger import log

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


def create_locations(db: Session):
    """Create locations"""
    for name in LOCATIONS:
        location = db.scalar(select(m.Location).where(m.Location.name_en == name["en"]))
        if not location:
            location = m.Location(
                name_en=name["en"],
                name_hebrew=name["hebrew"],
            )
            db.add(location)
    db.commit()
    log(log.INFO, "Locations [%d] were created", len(LOCATIONS))
