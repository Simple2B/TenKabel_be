from sqlalchemy.orm import Session

from tests.fixture import TestData

import app.model as m


def create_test_superuser(db, test_data):
    db.add(
        m.SuperUser(
            email=test_data.test_superuser.email,
            username=test_data.test_superuser.email,
            password=test_data.test_superuser.password,
        )
    )


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

    for notification in test_data.test_notifications_applications:
        db.add(
            m.Notification(
                user_id=notification.user_id,
                entity_id=notification.entity_id,
                type=notification.type,
            )
        )

    for notification in test_data.test_notifications_jobs:
        db.add(
            m.Notification(
                user_id=notification.user_id,
                entity_id=notification.entity_id,
                type=notification.type,
            )
        )

    db.commit()
