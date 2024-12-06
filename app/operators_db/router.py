from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.operators_db.methods_dao import (
    add_one_node,
    add_one_operator,
    get_nodes,
    get_operator,
    upd_operator,
    add_all_operators,
    check_base
)
from app.operators_db.schemas import SNodeAdd, SOperatorAdd, SOperatorGet, SOperatorUpdate
from app.users.dependensies import get_current_user

router = APIRouter(prefix='/operators', tags=['Работа с базой данных'], dependencies=[Depends(get_current_user)])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index_operators.html", {"request": request})


@router.post('/add_node')
async def add_node(node: SNodeAdd):
    check = await add_one_node(node.model_dump())
    if check:
        return {'message': 'Узел добавлен', 'node': node}
    return {'message': 'Ошибка при добавлении узла'}


@router.post('/add_operator')
async def add_operator(operator: SOperatorAdd):
    check = await add_one_operator(operator.model_dump())
    if check:
        return {'message': 'Оператор добавлен', 'node': operator}
    return {'message': 'Ошибка при добавлении оператора'}


@router.post('/add_all_operators')
async def add_operators():
    check = await check_base()
    if check:
        return {'message': 'БД не пустая'}
    operators = await add_all_operators()
    if operators:
        return {'message': 'Операторы добавлены', 'node': operators}
    return {'message': 'Ошибка при добавлении операторов'}


@router.get('/get_node')
async def get_node():
    result = await get_nodes()
    return result


@router.get("/get_operator")
async def get_parameter(param1: int, param2: int):
    params = SOperatorGet(node_id=param1, tg_number=param2)
    operator = await get_operator(params.model_dump())
    if operator is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Нет такой ТГ в БД')
    return {'operator_name': operator.name, 'tg_number': operator.tg_number, 'cic': operator.CIC}


@router.get("/choices")
async def get_choices():
    result = await get_nodes()
    return {"choices": [choice for choice in result]}


@router.put('/update_operator')
async def update_operator(values: SOperatorUpdate):
    filter_dict = {'node_id': values.node_id, 'tg_number': values.tg_number}
    values_dict = {'name': values.name, 'CIC': values.CIC}
    result = await upd_operator(filter_dict, values_dict)
    if result:
        return {'data': 'Оператор обновлен', 'operator': result}
    return {'message': 'Ошибка при обновлении оператора'}
