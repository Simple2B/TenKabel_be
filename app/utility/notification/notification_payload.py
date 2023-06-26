from app import schema as s
from app import model as m


def get_notification_payload(notification_type: s.NotificationType, job: m.Job):
    return s.PushNotificationPayload(
        notification_type=notification_type,
        job_uuid=job.uuid,
        job_name=job.name,
        job_price=job.payment,
        job_time=job.time,
        job_area=job.city,
        job_commission=job.commission,
        worker_name=job.worker.first_name if job.worker else "",
        owner_name=job.owner.first_name,
    )
