from fastapi import APIRouter, HTTPException, status, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.methods_dao import get_user, add_user
from app.users.schemas import SUserRegister

router = APIRouter(prefix='/auth', tags=['Auth'])
templates = Jinja2Templates(directory='app/templates')


@router.get("/", response_class=HTMLResponse, summary="Страница авторизации")
async def auth(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@router.post('/register/')
async def register_user(user_data: SUserRegister) -> dict:
    user = await get_user(name=user_data.name)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    hashed_password = get_password_hash(user_data.password)
    await add_user(name=user_data.name, hashed_password=hashed_password)
    return {'message': 'Вы успешно зарегистрированы!'}


@router.post('/login/')
async def login_user(response: Response, user_data: SUserRegister):
    check = await authenticate_user(user_data=user_data)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверный логин или пароль')
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Авторизация успешна!'}


@router.post('/logout/')
async def logout_user(response: Response):
    response.delete_cookie(key='users_access_token')
    return {'message': 'Пользователь успешно вышел из системы'}
