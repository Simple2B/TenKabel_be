import time
import json

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from sqladmin import Admin

from app.database import get_engine
from app.router import router
from app.admin import authentication_backend, pages
from app.logger import log
from app.schema.enums import DevicePlatform
from app.config import Settings, get_settings

engine = get_engine()

app = FastAPI()

admin: Admin = Admin(
    app=app,
    authentication_backend=authentication_backend,
    engine=engine,
    # templates_dir="app/templates/admin",
)


app.include_router(router)
templates = Jinja2Templates(directory="app/templates")
views = [
    pages.UserAdmin,
]
for view in views:
    admin.add_view(view)


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
