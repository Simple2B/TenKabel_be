from app import schema as s
from app.model import Application, Job
from app.logger import log


def get_notification_payload(
    notification_type: s.NotificationType,
    job: Job,
    application: Application | None = None,
):
    if job.worker:
        worker_name = (
            job.worker.first_name if job.worker.first_name else job.worker.email
        )
    elif application:
        worker_name = (
            application.worker.first_name
            if application.worker.first_name
            else application.worker.email
        )
    else:
        worker_name = ""
    log(log.INFO, "Notification type: %s", notification_type)
    return s.PushNotificationPayload(
        notification_type=notification_type,
        job_uuid=job.uuid,
        job_name=job.name,
        job_price=job.payment,
        job_time=job.time,
        job_area=", ".join([location.name_en for location in job.regions]),
        job_commission=job.commission,
        worker_name=worker_name,
        owner_name=job.owner.first_name,
    )
