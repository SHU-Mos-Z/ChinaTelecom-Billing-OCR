from Tools.UploadTools import *
from fastapi import APIRouter, File

group_urls = APIRouter()


@group_urls.post("/upload_files/")
async def upload_pdfs_ofds_photos(user_id: str, files: List[UploadFile] = File(...)):
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(Worker.worker_id == user_id)
        if query.first() is None:
            return {'msg': '当前账户非法，无法上传'}
        temp_dir = './uploaded_files/temp'
        save_dir = './uploaded_files/saved'
        return await extract_and_upload_files(user_id, files, conn, temp_dir, save_dir)
