from typing import List

from fastapi import APIRouter, Request, UploadFile, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, StreamingResponse

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
    return JSONResponse(
        content={"success": True, "message": "Файлы успешно загружены!."}, status_code=200)


@router.get('/result')
async def make_result(not_counted: dict = Depends(calculate_load)):
    return JSONResponse(content={'success': True, 'not_counted': not_counted})


@router.get('/download_files')
async def download_files():
    files_names, path_list, date_loading = await get_result_path()
    zip_buffer = await get_zip_file(files_names, path_list)
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={date_loading}.zip"}
    )
