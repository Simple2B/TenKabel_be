from fastapi import APIRouter, status, HTTPException
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError

from app.logger import log

notification_router = APIRouter(prefix="/notify", tags=["Notification"])


@notification_router.post("", status_code=status.HTTP_201_CREATED)
def create_notification(
    device_token: str,
):
    message = messaging.Message(
        notification=messaging.Notification(title="Привіт", body="Hello World!"),
        token=device_token,
    )
    try:
        messaging.send(message=message)
        log(log.INFO, "SENDED")
        return {"status": "should be done"}

    except FirebaseError:
        log(log.ERROR, "Error while sending message")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error while sending message"
        )

    except ValueError:
        log(log.ERROR, "Message arguments invalid")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Message arguments invalid"
        )
