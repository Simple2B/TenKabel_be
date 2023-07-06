from invoke import task


@task
def collecting_fee(_):
    from app.controller.celery import pay_plus_fee

    pay_plus_fee.apply()
