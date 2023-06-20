import firebase_admin

from fastapi import status, HTTPException
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError

from app.logger import log


class PushHandler:
    def __init__(self):
        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)

    def send_notification(self, device_tokens: list[str], title: str, body: str):
        message = messaging.MulticastMessage(
            # notification=messaging.Notification(title=title, body=body),
            tokens=device_tokens,
            data={"title": title, "body": body},
            android=messaging.AndroidConfig(
                ttl=3600,
                priority="high",
            ),
        )

        try:
            messaging.send_multicast(message=message)
            log(log.INFO, "SENDED")
            return {"status": "should be done"}

        except FirebaseError:
            log(log.ERROR, "Error while sending message")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while sending message",
            )

        except ValueError:
            log(log.ERROR, "Message arguments invalid")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Message arguments invalid"
            )
