# FastApi.app

Here you can find basic app with PostgreSQL

## Migrations

### Create new migration revision

```bash
alembic revision -m '<message>' --autogenerate
```

### DB migrate

```bash
alembic upgrade head
```
### init db (for development)
```bash
./clear_prepare_db.sh
inv create-jobs
```
<!-- execute all test users -->
```bash
inv shell
# example:
users = db.scalars(sa.select(m.User).order_by(m.User.id)).all()
```
