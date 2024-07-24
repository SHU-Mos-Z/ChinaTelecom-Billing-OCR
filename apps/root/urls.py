# from Tools.UploadTools import *
from fastapi import APIRouter
from Tools.SearchTools import *


root_urls = APIRouter()


# @root_urls.post("/upload_files/")
# async def upload_pdfs_ofds_photos(user_id: str, files: List[UploadFile] = File(...)):
#     with Session(bind=engine) as conn:
#         query = conn.query(Worker.worker_id).where(
#             get_where_conditions([Worker.worker_id, Worker.role], user_id, 'system_manager'))
#         if query.first() is None:
#             return {'msg': '当前账户非法或者权限过低，禁止查询'}
#         temp_dir = './uploaded_files/temp'
#         save_dir = './uploaded_files/saved'
#         return await extract_and_upload_files(user_id, files, conn, temp_dir, save_dir)


@root_urls.post("/search_worker/", summary='获取所有班组的员工列表')
async def search_worker(user_id: str) -> Dict:
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(
            get_where_conditions([Worker.worker_id, Worker.role], user_id, 'system_manager'))
        if query.first() is None:
            return {'msg': '当前账户非法或者权限不匹配，禁止查询'}
        return await search_all_worker_for_root(conn=conn)


@root_urls.post("/search_quota/", summary='根据年份，给出每个班组所有员工每个月的额度')
async def search_quota(user_id: str, target_year: str = None) -> Dict:
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(
            get_where_conditions([Worker.worker_id, Worker.role], user_id, 'system_manager'))
        if query.first() is None:
            return {'msg': '当前账户非法或者权限不匹配，禁止查询'}
        return await search_quota_for_root(conn, target_year)


@root_urls.post("/search_service/", summary='给出发票上交状况页面表格')
async def search_service_hand_in(user_id: str, search_info: SearchServiceInfoRoot) -> Dict | List[Dict]:
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(
            get_where_conditions([Worker.worker_id, Worker.role], user_id, 'system_manager'))
        if query.first() is None:
            return {'msg': '当前账户非法或者权限不匹配，禁止查询'}
        return await search_service_year_season_for_root(conn, search_info)
