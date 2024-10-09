import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.loading.router import router as loading_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount('/static', StaticFiles(directory='app/static'), 'static')
app.include_router(loading_router)

