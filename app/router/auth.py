# from shutil import unregister_archive_format
from fastapi import APIRouter, Depends, HTTPException, status
import sqlalchemy as sa
from sqlalchemy import select, exists
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from app.dependency import get_current_user
from app.database import get_db
import app.model as m
import app.schema as s
from app.oauth2 import create_access_token
from app.logger import log
from app.controller import create_payplus_customer, delete_device
from app.config import get_settings, Settings

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login-by-phone", response_model=s.Token)
def login_by_phone(
    user_credentials: s.AuthUser,
    db: Session = Depends(get_db),
):
    user: m.User = m.User.authenticate_with_phone(
        db,
        user_credentials.phone,
        user_credentials.password,
        user_credentials.country_code,
    )

    if not user:
        log(log.ERROR, "User [%s] was not authenticated", user_credentials.phone)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    access_token: str = create_access_token(data={"user_id": user.id})
    log(log.INFO, "Access token for User [%s] generated", user.phone)
    return s.Token(
        access_token=access_token,
        token_type="Bearer",
    )


@auth_router.post(
    "/sign-up", status_code=status.HTTP_201_CREATED, response_model=s.User
)
def sign_up(
    data: s.UserSignUp,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if db.scalar(exists().where(m.User.phone == data.phone).select()):
        log(log.ERROR, "User [%s] already exist", data.phone)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exist",
        )

    user: m.User = m.User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        password=data.password,
        phone=data.phone,
        country_code=data.country_code,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as e:
        log(log.ERROR, "Error signing up user - [%s]\n%s", data.phone, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error while signing up"
        )
    log(log.INFO, "User [%s] signed up", user.phone)

    profession: m.Profession | None = db.scalar(
        select(m.Profession).where(m.Profession.id == data.profession_id)
    )

    if profession:
        db.add(
            m.UserProfession(
                user_id=user.id,
                profession_id=profession.id,
            )
        )
        log(log.INFO, "User's profession created [%s]", profession.name_en)

    locations: list[m.Location] = [
        location
        for location in db.scalars(
            select(m.Location).where(m.Location.id.in_(data.locations))
        )
    ]
    for location in locations:
        db.add(m.UserLocation(user_id=user.id, location_id=location.id))
        db.flush()

    log(log.INFO, "User's locations created [%d]", len(user.locations))
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error post sign up user - [%s]\n%s", data.phone, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error storing user data"
        )

    create_payplus_customer(user, settings, db)

    log(log.INFO, "User [%s] COMPLETELY signed up", user.phone)
    return user


@auth_router.put("/verify", status_code=status.HTTP_200_OK, response_model=s.User)
def verify(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    current_user.is_verified = True

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error signing up user [%s] - ", current_user.phone, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error while signing up"
        )

    log(log.INFO, "User [%s] is verified", current_user.phone)

    return current_user


@auth_router.post("/apple", status_code=status.HTTP_200_OK, response_model=s.Token)
def apple_auth(
    data: s.AppleAuthUser,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not data.email:
        log(log.INFO, "Email is required")
        raise HTTPException(
            status=status.HTTP_409_CONFLICT,
            detail="Email is required",
        )
    user: m.User | None = (
        db.query(m.User)
        .filter(sa.func.lower(m.User.email) == sa.func.lower(data.email))
        .first()
    )

    password = "*"
    country_code = "IL"

    if not user:
        if not data.display_name:
            first_name = data.email.split("@")[0] if data.email else ""
            last_name = ""

        else:
            names = data.display_name.split(" ")
            if len(names) > 1:
                first_name, last_name = names[0], " ".join(names[1:])
            else:
                first_name, last_name = names[0], ""

        user: m.User = m.User(
            email=data.email,
            first_name=first_name,
            last_name=last_name,
            username=data.email,
            apple_uid=data.uid,
            password=password,
            is_verified=True,
            country_code=country_code,
        )
        db.add(user)
        db.flush()
        if data.first_name:
            user.first_name = data.first_name
        if data.last_name:
            user.last_name = data.last_name
        if data.country_code:
            user.country_code = data.country_code
        if data.phone:
            user.phone = data.phone
        if data.locations:
            locations: list[m.Location] = [
                location
                for location in db.scalars(
                    select(m.Location).where(m.Location.id.in_(data.locations))
                )
            ]
            for location in locations:
                db.add(m.UserLocation(user_id=user.id, location_id=location.id))
                db.flush()
        if data.professions:
            professions: list[m.Profession] = [
                profession
                for profession in db.scalars(
                    select(m.Profession).where(m.Profession.id.in_(data.professions))
                )
            ]
            for profession in professions:
                db.add(m.UserProfession(user_id=user.id, profession_id=profession.id))
                db.flush()

        try:
            db.commit()
        except SQLAlchemyError as e:
            log(log.INFO, "Error - [%s]", e)
            raise HTTPException(
                status=status.HTTP_409_CONFLICT,
                detail="Error while saving user via Apple",
            )

        log(
            log.INFO,
            "User [%s] has been created (via Apple account))",
            user.email,
        )

    user: m.User = m.User.authenticate(
        db,
        user.email,
        user.password,
    )

    if not user:
        log(log.ERROR, "User [%s] was not authenticated", data.email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    create_payplus_customer(user, settings, db)

    access_token: str = create_access_token(data={"user_id": user.id})
    log(log.INFO, "Access token for User [%s] generated", user.email)
    return s.Token(
        access_token=access_token,
        token_type="Bearer",
    )


@auth_router.post("/google", status_code=status.HTTP_200_OK, response_model=s.Token)
def google_auth(
    data: s.GoogleAuthUser,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    user: m.User | None = (
        db.query(m.User)
        .filter(sa.func.lower(m.User.email) == sa.func.lower(data.email))
        .first()
    )
    # TODO: alot hardcoding there
    password = "*"
    country_code = "IL"

    if not data.display_name:
        first_name = data.first_name
        last_name = data.last_name

    if not user:
        first_name, last_name = data.first_name, data.last_name
        if not first_name:
            if not data.display_name:
                data.display_name = data.email.split("@")[0]
            names = data.display_name.split(" ")
            if len(names) > 1:
                first_name, last_name = names[0], " ".join(names[1:])
            else:
                first_name, last_name = names[0], ""

        user: m.User = m.User(
            email=data.email,
            first_name=first_name,
            last_name=last_name,
            username=data.email,
            google_openid_key=data.uid,
            password=password,
            is_verified=True,
            country_code=country_code,
        )
        db.add(user)
        db.flush()
        if data.first_name:
            user.first_name = data.first_name
        if data.last_name:
            user.last_name = data.last_name
        if data.country_code:
            user.country_code = data.country_code
        if data.phone:
            user.phone = data.phone
        if data.locations:
            locations: list[m.Location] = [
                location
                for location in db.scalars(
                    select(m.Location).where(m.Location.id.in_(data.locations))
                )
            ]
            for location in locations:
                db.add(m.UserLocation(user_id=user.id, location_id=location.id))
                db.flush()
        if data.professions:
            professions: list[m.Profession] = [
                profession
                for profession in db.scalars(
                    select(m.Profession).where(m.Profession.id.in_(data.professions))
                )
            ]
            for profession in professions:
                db.add(m.UserProfession(user_id=user.id, profession_id=profession.id))
                db.flush()

        try:
            db.commit()
        except SQLAlchemyError as e:
            log(log.INFO, "Error - [%s]", e)
            raise HTTPException(
                status=status.HTTP_409_CONFLICT,
                detail="Error while saving creating a user",
            )

        log(
            log.INFO,
            "User [%s] has been created (via Google account))",
            user.email,
        )

    user: m.User = m.User.authenticate(
        db,
        user.email,
        user.password,
    )

    if not user:
        log(log.ERROR, "User [%s] was not authenticated", data.email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    create_payplus_customer(user, settings, db)

    access_token: str = create_access_token(data={"user_id": user.id})
    log(log.INFO, "Access token for User [%s] generated", user.email)
    return s.Token(
        access_token=access_token,
        token_type="Bearer",
    )


@auth_router.post(
    "/logout", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)]
)
def logout(
    device: s.LogoutIn,
    db: Session = Depends(get_db),
):
    delete_device(device, db)


@auth_router.get(
    "/user/pre-validate", status_code=status.HTTP_200_OK, response_model=s.PreValidate
)
def pre_validate_user(
    field: str,
    value: str,
    db: Session = Depends(get_db),
):
    if not hasattr(m.User, field):
        log(log.INFO, "Invalid field [%s]", field)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid field",
        )
    user = db.scalar(
        select(m.User).where(
            sa.func.lower(getattr(m.User, field)) == sa.func.lower(value)
        )
    )
    if user:
        return s.PreValidate(isExist=True, message="User already exist")

    return s.PreValidate(isExist=False, message="User doesn't exist")
