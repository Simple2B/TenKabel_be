from invoke import task
from sqlalchemy import select
from fastapi import status


from app.model import User, Profession, Location, UserLocation, UserProfession
from app.logger import log

TEST_USER_PHONE = "001"
TEST_PASSWORD = "pass"
TEST_EMAIL_END = "@test.com"


@task
def create_user(
    _,
    telephone: str = TEST_USER_PHONE,
    password: str = TEST_PASSWORD,
    location_id: int | None = None,
    profession_id: int | None = None,
):
    """create user with given telephone and password

    Args:
        telephone (str, optional): user phone. Default value is "001".
        password (str, optional): user password. Default value is "pass".
        location_id (int, optional): user location id. Default value is None.
        profession_id (int, optional): user profession id. Default value is None.
    """

    from app.database import db

    first_name = "FIRST" + telephone
    last_name = "LAST" + telephone
    email = first_name + TEST_EMAIL_END

    with db.begin() as conn:
        query = select(User).where(User.email == email)
        user = conn.scalar(query)
        if not user:
            user: User = User(
                phone=telephone,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_verified=True,
                country_code="LI",
            )
            conn.add(user)
            profession: Profession | None = conn.scalar(
                select(Profession).where(Profession.id == profession_id)
            )

            if profession:
                conn.add(
                    UserProfession(
                        user_id=user.id,
                        profession_id=profession_id,
                    )
                )
                log(log.INFO, "User's profession created [%s]", profession.name_en)

            location: Location | None = conn.scalar(
                select(Location).where(Location.id == location_id)
            )

            if location:
                conn.add(
                    UserLocation(
                        user_id=user.id,
                        location_id=location_id,
                    )
                )
                log(log.INFO, "User's location created [%s]", location.name_en)

            conn.commit()
            log(
                log.INFO,
                "%s %s - %s created",
                first_name,
                last_name,
                email,
            )
        else:
            log(log.WARNING, "User %s already exists", email)


@task
def login_user(
    _,
    telephone: str = TEST_USER_PHONE,
    password: str = TEST_PASSWORD,
):
    """user login with given telephone and password

    Args:
        telephone (str, optional): user phone. Defaults to "001".
        password (str, optional): user password. Defaults to "pass".
    """
    from fastapi.testclient import TestClient
    from app.main import app
    from app import schema as s

    with TestClient(app) as client:
        user_data = s.AuthUser(
            phone=telephone,
            password=password,
            country_code="LI",
        )

        response = client.post(
            "/api/auth/login-by-phone",
            json=user_data.dict(),
        )
        if response.status_code != status.HTTP_200_OK:
            log(log.ERROR, "User login failed")
            return

        token = s.Token.parse_obj(response.json())
        log(log.INFO, "User token: %s", token.access_token)
        return token.access_token
