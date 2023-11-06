from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

import app.model as m
import app.schema as s

from tests.fixture import TestData


def test_file_methods(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    filename = "test_avatar_1.png"
    file = open(f"tests/utility/images/{filename}", "rb")

    response = client.post(
        "api/files",
        files={
            "file": file,
        },
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    file: m.File = db.scalars(
        select(m.File).where(m.File.original_filename == filename)
    ).first()
    assert file
    assert file.user.email == test_data.test_authorized_users[0].email

    # getting attachment
    response = client.get(
        f"api/files/{file.uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_data = s.FileOut(**response.json())
    assert resp_data.uuid == file.uuid

    response = client.delete(
        f"api/files/{file.uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    file: m.File = db.scalars(select(m.File).where(m.File.uuid == file.uuid)).first()

    assert not file
