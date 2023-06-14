import enum


class Status(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    JOB_IS_FINISHED = "job_is_finished"
