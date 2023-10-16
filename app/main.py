import jinja2
import time
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# patch https://jinja.palletsprojects.com/en/3.0.x/changes/
# pass_context replaces contextfunction and contextfilter.
jinja2.contextfunction = jinja2.pass_context
# flake8: noqa F402

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from sqladmin import Admin

from app.database import get_engine
from app.router import router
from app.admin import authentication_backend
from app.logger import log


engine = get_engine()

app = FastAPI()

admin = Admin(
    app=app,
    authentication_backend=authentication_backend,
    engine=engine,
    templates_dir="app/templates/admin",
)

sql_admin = Admin(app, engine)

app.include_router(router)


templates = Jinja2Templates(directory="app/templates")


@app.get("/policy", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    log(log.INFO, "Time estimated - [%s]", process_time)
    return response


@app.get("/")
def root():
    return RedirectResponse("/docs")
