from sqlalchemy.orm import Session

from tests.fixture import TestData

import app.model as m


def create_test_superuser(db, test_data):
    db.add(
        m.SuperUser(
            email=test_data.test_superuser.email,
            username=test_data.test_superuser.email,
            password=test_data.test_superuser.password,
            country_code=test_data.test_superuser.country_code,
        )
    )
    db.commit()


def fill_db_by_test_data(db: Session, test_data: TestData):
    print("Filling up db with fake data")
    create_test_superuser(db, test_data)
    for u in test_data.test_users:
        db.add(
            m.User(
                first_name=u.username,
                last_name=u.username,
                username=u.username,
                email=u.email,
                password=u.password,
                is_verified=u.is_verified,
                phone=u.phone,
                country_code=u.country_code,
            )
        )
        db.commit()
    for u in test_data.test_authorized_users:
        db.add(
            m.User(
                first_name=u.username,
                last_name=u.username,
                username=u.username,
                email=u.email,
                password=u.password,
                is_verified=u.is_verified,
                phone=u.phone,
                country_code=u.country_code,
            )
        )
        db.commit()
        # TODO
        # professions and locations for this users !!!
