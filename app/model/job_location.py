import sqlalchemy as sa
from app.database import db


jobs_locations = sa.Table(
    "jobs_locations",
    db.Model.metadata,
    sa.Column("job_id", sa.ForeignKey("jobs.id"), primary_key=True),
    sa.Column("location_id", sa.ForeignKey("locations.id"), primary_key=True),
)


class JobLocation(db.Model):
    __tablename__ = "jobs_locations"
