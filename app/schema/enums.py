import enum


class JobStatus(enum.Enum):
    PENDING = 1
    IN_PROGRESS = 2
    JOB_IS_FINISHED = 3
