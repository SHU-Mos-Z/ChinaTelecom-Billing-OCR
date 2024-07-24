from fastapi import APIRouter
# from Tools.UploadTools import *
from Tools.SearchTools import *

center_urls = APIRouter()


# @center_urls.post("/upload_files/")
# async def upload_pdfs_ofds_photos(user_id: str, files: List[UploadFile] = File(...)):
#     with Session(bind=engine) as conn:
#         query = conn.query(Worker.worker_id).where(
#             get_where_conditions([Worker.worker_id, Worker.role], user_id, 'center_manager'))
#         if query.first() is None:
#             return {'msg': '当前账户非法或者权限过低，禁止查询'}
#         temp_dir = './uploaded_files/temp'
#         save_dir = './uploaded_files/saved'
#         return await extract_and_upload_files(user_id, files, conn, temp_dir, save_dir)


@center_urls.post("/search_quota/", summary='输入上传和开票的时间范围，得到中心管理界面所有班组的表格内信息')
async def search_quota(user_id: str, search_info: SearchTimeZone):
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(
            get_where_conditions([Worker.worker_id, Worker.role], user_id, 'center_manager'))
        if query.first() is None:
            return {'msg': '当前账户非法或者权限不匹配，禁止查询'}
        return await search_quota_class_for_center(conn, search_info)

