from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

import app.model as m
import app.schema as s

from tests.fixture import TestData
from tests.utility import (
    create_attachments,
    create_locations,
    create_professions,
    create_jobs,
    create_jobs_for_user,
    fill_test_data,
)


def test_attachment_methods(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    create_professions(db)
    create_locations(db)
    fill_test_data(db)
    create_jobs(db)
    create_attachments(db)

    user: m.User = db.scalar(
        select(m.User).where(m.User.phone == test_data.test_authorized_users[0].phone)
    )
    create_jobs_for_user(db, user.id, 1)

    job_id = db.scalars(select(m.Job.id).where(m.Job.owner_id == user.id)).first()
    files = db.scalars(select(m.File).where(m.File.user_id == user.id)).all()

    request_data = s.AttachmentIn(
        job_id=job_id, file_uuids=[file.uuid for file in files]
    )
    response = client.post(
        "api/attachments",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    attachment: m.Attachment = db.scalars(
        select(m.Attachment).where(
            and_(m.Attachment.file_id == files[0].id, m.Attachment.user_id == user.id)
        )
    ).first()
    assert attachment
    assert attachment.job_id == job_id
    # getting attachment
    response = client.get(
        f"api/attachments/{attachment.uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_data = s.AttachmentOut(**response.json())
    assert resp_data.uuid == attachment.uuid

    response = client.delete(
        f"api/attachments/{attachment.uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    attachment: m.Attachment = db.scalars(
        select(m.Attachment).where(m.Attachment.uuid == attachment.uuid)
    ).first()
    assert attachment.is_deleted
