from sqlalchemy.orm import Session

from app import model as m
from app.utility import generate_uuid


def generate_customer_uid(user: m.User, db: Session) -> str:
    if user.payplus_customer_uid:
        return user.payplus_customer_uid

    user.payplus_customer_uid = generate_uuid()
    db.commit()
    db.refresh(user)

    return user.payplus_customer_uid
