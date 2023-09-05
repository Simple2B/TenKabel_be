from app import schema as s
from app import model as m


def get_notification_payload(
    notification_type: s.NotificationType,
    job: m.Job,
    application: m.Application | None = None,
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
