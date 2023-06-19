import enum


class JobStatus(enum.Enum):
    PENDING = 1
    APPROVED = 2
    IN_PROGRESS = 3
    JOB_IS_FINISHED = 4
