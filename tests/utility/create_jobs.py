import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import select
from faker import Faker

from app import model as m
from app import schema as s
from app.logger import log

from .create_locations import create_locations

fake: Faker = Faker()


TEST_JOBS_NUM = 100
TEST_USER_JOBS_NUM = 10


JOBS_LIST = [
    "mechanic",
    "courier",
    "medic",
    "deliveryman",
    "teacher",
    "handyman",
]

TEST_REGIONS = [
    "Goosh Dan, Sharon",
    "Binyamin, Shomron",
    "Etzion" "Haifa",
    "Kiryat Shmona",
    "Jerusalem",
]

TEST_LOCATIONS = [
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


def create_jobs(db: Session, test_jobs_num: int = TEST_JOBS_NUM):
    worker_ids = [worker.id for worker in db.scalars(select(m.User)).all()]
    professions = db.scalars(select(m.Profession)).all()
    locations_ids = [location.id for location in db.scalars(select(m.Location)).all()]
    if not locations_ids:
        create_locations(db)
        locations_ids = [
            location.id for location in db.scalars(select(m.Location)).all()
        ]

    created_jobs: list = list()
    start = datetime.now()
    date_list = [start + timedelta(days=x) for x in range(3)]
    date_list += [start - timedelta(days=x) for x in range(3)]
    for _ in range(test_jobs_num):
        profession = random.choice(professions)
        job: m.Job = m.Job(
            owner_id=random.choice(worker_ids),
            worker_id=random.choice(worker_ids),
            profession_id=profession.id,
            name=profession.name_en,
            description=fake.unique.sentence(),
            payment=random.randint(0, 100),
            commission=random.uniform(0, 10),
            city=random.choice(TEST_REGIONS),
            time=datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            who_pays=random.choice([e for e in s.Job.WhoPays]),
            customer_first_name=fake.first_name(),
            customer_last_name=fake.last_name(),
            customer_phone=fake.unique.phone_number(),
            customer_street_address=fake.address(),
            # random date between
            created_at=random.choice(date_list),
        )
        db.add(job)
        created_jobs.append(job)
        db.flush()
        job.set_enum(random.choice([e for e in s.enums.JobStatus]), db)
        job.set_enum(random.choice([e for e in s.enums.PaymentStatus]), db)
        job.set_enum(random.choice([e for e in s.enums.CommissionStatus]), db)
        locations = random.sample(locations_ids, random.randint(1, 3))
        for location in locations:
            job_location: m.JobLocation = m.JobLocation(
                location_id=location, job_id=job.id
            )
            db.add(job_location)

    for job in created_jobs:
        # job status can't be pending with existing worker
        if job.status == s.enums.JobStatus.PENDING:
            job.worker_id = None
        # owner can't work on his own job
        while job.owner_id == job.worker_id:
            job.worker_id = random.choice(worker_ids[:-1])

    log(log.INFO, "Jobs created - %s", test_jobs_num)
    db.commit()


def create_jobs_for_user(
    db: Session,
    user_id: int,
    test_jobs_num: int = TEST_USER_JOBS_NUM,
    logs_off: bool = False,
):
    user = db.scalar(select(m.User).where(m.User.id == user_id))
    if not user:
        log(log.INFO, "User with id [%s] doesn't exist", user_id)
        raise ValueError
    worker_ids = [
        worker.id for worker in db.scalars(select(m.User)).all() if worker.id != user_id
    ] + [None]
    professions = db.scalars(select(m.Profession)).all()
    locations_ids = [location.id for location in db.scalars(select(m.Location)).all()]
    if not locations_ids:
        create_locations(db)
        locations_ids = [
            location.id for location in db.scalars(select(m.Location)).all()
        ]
    created_jobs = []

    for _ in range(test_jobs_num):
        profession = random.choice(professions)
        job1: m.Job = m.Job(
            owner_id=user_id,
            worker_id=random.choice(worker_ids),
            profession_id=profession.id,
            name=profession.name_en,
            description=fake.sentence(),
            payment=random.randint(0, 100),
            commission=random.uniform(0, 10),
            city=random.choice(TEST_REGIONS),
            time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            who_pays=random.choice([e for e in s.Job.WhoPays]),
            customer_first_name=fake.first_name(),
            customer_last_name=fake.last_name(),
            customer_phone=fake.phone_number(),
            customer_street_address=fake.address(),
        )
        db.add(job1)
        db.flush()
        job1.set_enum(random.choice([e for e in s.enums.JobStatus]), db)
        job1.set_enum(random.choice([e for e in s.enums.PaymentStatus]), db)
        job1.set_enum(random.choice([e for e in s.enums.CommissionStatus]), db)
        locations = random.sample(locations_ids, random.randint(1, 3))
        for location in locations:
            job_location: m.JobLocation = m.JobLocation(
                location_id=location, job_id=job1.id
            )
            db.add(job_location)

        job2: m.Job = m.Job(
            owner_id=random.choice(worker_ids[:-1]),
            worker_id=user_id,
            profession_id=profession.id,
            name=profession.name_en,
            description=fake.sentence(),
            payment=random.randint(0, 100),
            commission=random.uniform(0, 10),
            city=random.choice(TEST_REGIONS),
            time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            who_pays=random.choice([e for e in s.Job.WhoPays]),
            customer_first_name=fake.unique.first_name(),
            customer_last_name=fake.unique.last_name(),
            customer_phone=fake.unique.phone_number(),
            customer_street_address=fake.address(),
        )
        db.add(job2)
        db.flush()
        job2.set_enum(random.choice([e for e in s.enums.JobStatus]), db)
        job2.set_enum(random.choice([e for e in s.enums.PaymentStatus]), db)
        job2.set_enum(random.choice([e for e in s.enums.CommissionStatus]), db)
        locations = random.sample(locations_ids, random.randint(1, 3))
        for location in locations:
            job_location: m.JobLocation = m.JobLocation(
                location_id=location, job_id=job2.id
            )
            db.add(job_location)
        created_jobs.append(job1)
        created_jobs.append(job2)

    for job in created_jobs:
        # job status can't be pending with existing worker
        if job.worker_id and job.status == s.enums.JobStatus.PENDING:
            job.worker_id = None
        # job progress cant exist with no worker
        elif not job.worker_id and job.status != s.enums.JobStatus.PENDING:
            job.worker_id = random.choice(worker_ids[:-1])
        # owner can't work on his own job
        while job.owner_id == job.worker_id:
            job.worker_id = random.choice(worker_ids)

    db.commit()
    if not logs_off:
        log(log.INFO, "Jobs for user [%s] created - %s", user_id, test_jobs_num)
