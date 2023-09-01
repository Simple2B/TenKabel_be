import base64

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

import app.model as m
import app.schema as s

from tests.fixture import TestData
from tests.utility import (
    create_attachments,
)


def test_create_attachment(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    create_attachments(db)

    filename = "test_avatar_1.png"
    with open(f"tests/utility/images/{filename}", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    request_data = s.AttachmentIn(file=encoded_string, filename=filename)
    response = client.post(
        "api/attachments",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    attachment = db.scalars(
        select(m.Attachment).where(m.Attachment.original_filename == filename)
    ).first()
    assert attachment
    assert attachment.user.email == test_data.test_authorized_users[0].email
    # getting attachment
    response = client.get(
        f"api/attachments/{attachment.uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_data = s.AttachmentOut(**response.json())
    assert resp_data.uuid == attachment.uuid
