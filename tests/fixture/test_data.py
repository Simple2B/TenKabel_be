from typing import Generator

import pytest
from pydantic import BaseModel


class TestUser(BaseModel):
    __test__ = False

    username: str
    first_name: str | None
    last_name: str | None
    email: str
    password: str
    google_openid_key: str | None
    picture: str | None
    is_verified: bool | None = True
    phone: str | None
    rates: list | None


class TestRate(BaseModel):
    __test__ = False

    uuid: str | None
    giver_id: str
    user_id: str
    rate: str


class TestData(BaseModel):
    __test__ = False

    test_user: TestUser | None
    test_users: list[TestUser]
    test_rate: TestRate | None
    test_rates: list[TestRate]

    # authorized
    test_authorized_users: list[TestUser]
    test_superuser: TestUser | None


@pytest.fixture
def test_data() -> Generator[TestData, None, None]:
    yield TestData.parse_file("tests/test_data.json")
