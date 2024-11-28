from typing import List

from fastapi import APIRouter, Request, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

from app.utils.base import calculate_load
from app.utils.files import load_file, get_result_path, get_zip_file

router = APIRouter(prefix='/load', tags=['Расчет загрузки и формирование файлов'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/')
async def get_main_page(request: Request):
    return templates.TemplateResponse(name='index.html', context={'request': request})


@router.post('/upload_files')
async def upload_files(files: List[UploadFile]):
    for file in files:
        await load_file(file)
    return {"success": True, "message": "Файлы успешно загружены!!!."}


@router.get('/result')
async def make_result():
    try:
        not_counted = await calculate_load()

        return {'success': True, 'not_counted': not_counted}
    except FileNotFoundError as e:
        print(e)
        file = e.filename.split('/')[-1]
        raise HTTPException(status_code=422,
                            detail=f'Неверно назван исходный файл, должен называться: {file}')


@router.get('/download_files')
async def download_files():
    files_names, path_list, date_loading = await get_result_path()
    zip_buffer = await get_zip_file(files_names, path_list)
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={date_loading}.zip"}
    )
