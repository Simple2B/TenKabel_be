import time
import json

import jinja2
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# patch https://jinja.palletsprojects.com/en/3.0.x/changes/
# pass_context replaces contextfunction and contextfilter.
jinja2.contextfunction = jinja2.pass_context
# flake8: noqa F402

from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from sqladmin import Admin

from app.database import get_engine
from app.router import router
from app.admin import authentication_backend
from app.logger import log
from app.schema.enums import DevicePlatform
from app.config import Settings, get_settings

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


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    log(log.INFO, "Time estimated - [%s]", process_time)
    return response


@app.get("/policy", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


@app.get("/.well-known/apple-app-site-association")
def apple_app_link():
    with open("apple-app-site-association.json", "r") as file:
        data = json.load(file)
    return data


@app.get("/.well-known/assetlinks.json")
def android_app_link():
    with open("assetlinks.json", "r") as file:
        data = json.load(file)
    return data


@app.get("/.well-known/assetlinks.json")
def android_app_link():
    with open("assetlinks.json", "r") as file:
        data = json.load(file)
    return data


@app.get("/JobDetailed/{uuid}")
def redirect_to_store(
    uuid: str,
    platform: str = "",
    settings: Settings = Depends(get_settings),
):
    if platform == DevicePlatform.IOS.value:
        return RedirectResponse(settings.APP_STORE_LINK)
    return RedirectResponse(settings.PLAY_MARKET_LINK)


@app.get("/")
def root():
    return RedirectResponse("/docs")
