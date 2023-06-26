import firebase_admin

from fastapi import status, HTTPException
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError

from app import schema as s
from app.logger import log


class PushHandler:
    _is_initialized = False

    def __init__(self):
        if PushHandler._is_initialized:
            log(log.INFO, "Firebase was initialized")
            return

        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
        PushHandler._is_initialized = True

    def send_notification(self, message_data: s.PushNotificationMessage):
        if not message_data.device_tokens:
            log(log.INFO, "User has no tokens to push")
            return

        message = messaging.MulticastMessage(
            tokens=message_data.device_tokens,
            data={
                "notification_type": message_data.payload.notification_type.value,
                "job_uuid": message_data.payload.job_uuid,
            },
            android=messaging.AndroidConfig(
                ttl=3600,
                priority="high",
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        content_available=True,
                        mutable_content=True,
                    ),
                    headers={"apns-priority": "5"},
                ),
            ),
        )

        try:
            messaging.send_multicast(multicast_message=message)
            log(log.INFO, "Notification sended")
            return {"status": "should be done"}

        except FirebaseError:
            log(log.ERROR, "Error while sending message")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while sending message",
            )

        except (ValueError, TypeError):
            log(log.ERROR, "Message arguments invalid")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Message arguments invalid"
            )
