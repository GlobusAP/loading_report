import os
import zipfile
from io import BytesIO

from fastapi import UploadFile, HTTPException, status
from datetime import date


def get_path():
    return f'app/files_db/{date.today()}'


async def load_file(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Файл должен быть с расширением .csv'
        )
    path = get_path()
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
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


async def get_result_path():
    directory = 'app/files_db/results'
    files_names = sorted(os.listdir(directory))
    path_list = [f'{directory}/{file}' for file in files_names]
    date_loading = files_names[0].split('_')[-1].strip('.xlsx')
    return files_names, path_list, date_loading


async def get_zip_file(files_names: str, path_list: str, ):
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path, file_name in zip(path_list, files_names):
            zf.write(file_path, arcname=file_name)

    zip_buffer.seek(0)
    return zip_buffer
