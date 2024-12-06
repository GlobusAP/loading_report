import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.load_calculation.router import router as loading_router
from app.operators_db.router import router as operators_router
from app.users.exceptions import TokenExpiredException, TokenNoFoundException
from app.users.router import router as users_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount('/static', StaticFiles(directory='app/static'), 'static')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить запросы с любых источников. Можете ограничить список доменов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(loading_router)
app.include_router(operators_router)


@app.get('/')
async def redirect_to_auth():
    return RedirectResponse(url='/load')


@app.exception_handler(TokenExpiredException)
async def token_expired_exception(request: Request, ex: HTTPException):
    return RedirectResponse(url='/auth')


@app.exception_handler(TokenNoFoundException)
async def token_no_found_exception(request: Request, ex: HTTPException):
    return RedirectResponse(url='/auth')
