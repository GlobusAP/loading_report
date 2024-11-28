import os
import zipfile
from datetime import date, datetime
from io import BytesIO

from fastapi import UploadFile, HTTPException, status

from app.operators_db.schemas import SOperatorAdd


async def get_path(default_path: str = 'app/files_db'):
    path = f'{default_path}/{date.today()}'
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    return path


async def load_file(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Файл должен быть с расширением .csv'
        )
    path = await get_path()
    try:
        name = file.filename.split('.')[0].upper()
        contents = await file.read()
        with open(f'{path}/{name}.csv', 'wb') as f:
            f.write(contents)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='There was an error uploading the file'
        )
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}


async def get_date():
    directory = await get_path()
    files_names = os.listdir(directory)
    file = files_names[0]
    with open(f'{directory}/{file}', 'r', encoding='utf-8') as f:
        date_loading = datetime.strptime(f.readlines()[6:7][0].split(',')[0].strip('"'), '%d/%m/%Y %H:%M:%S')
    return date_loading


async def get_result_path():
    date_loading = await get_date()
    directory = await get_path(default_path='app/files_db/results')
    files_names = sorted(os.listdir(directory))
    path_list = [f'{directory}/{file}' for file in files_names
                 if file.split('_')[-1].strip('.xlsx') == str(date_loading.date())]
    return files_names, path_list, date_loading.date()


async def get_zip_file(files_names: str, path_list: str, ):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path, file_name in zip(path_list, files_names):
            zf.write(file_path, arcname=file_name)
    zip_buffer.seek(0)
    return zip_buffer


async def __get_operators(nodes):
    nodes = {node.name: node.id for node in nodes}
    names = sorted(os.listdir('app/files_db/CICs'))
    operators = []
    for name in names:
        with open(f'app/files_db/CICs/{name}', 'r', encoding='utf-8') as file:
            res = file.read()
            node_id = nodes.get(name.split('.')[0])

            for line in res.splitlines():
                k, v = line.split(',')

                tg_number = int(k.split('(')[-1].strip(')'))
                op = SOperatorAdd(tg_number=tg_number, name=k, CIC=int(v), node_id=node_id)
                operators.append(op)
    return operators
