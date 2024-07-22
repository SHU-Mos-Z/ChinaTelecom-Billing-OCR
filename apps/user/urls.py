from fastapi import APIRouter, File
from Tools.UploadTools import *
from Tools.SearchTools import *
from Tools.DataBaseTools import *
# from fastapi_limiter.depends import RateLimiter
import calendar

user_urls = APIRouter()


# @user_urls.post("/upload_files/")
# async def extract_and_upload_pdfs_ofds_photos(user_id: str, files: List[UploadFile] = File(...)):
#     with Session(bind=engine) as conn:
#         query = conn.query(Worker.worker_id).where(Worker.worker_id == user_id)
#         if query.first() is None:
#             return {'msg': '当前账户非法，无法上传'}
#         temp_dir = './uploaded_files/temp'
#         save_dir = './uploaded_files/saved'
#         return await extract_and_upload_files(user_id, files, conn, temp_dir, save_dir)


@user_urls.post("/show_file_info/")
async def get_files_info(user_id: str, files: List[UploadFile] = File(...)) -> List[Dict] | Dict:
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(Worker.worker_id == user_id)
        if query.first() is None:
            return {'msg': '当前账户非法，无法上传'}
        temp_dir = './uploaded_files/temp'
        save_dir = './uploaded_files/saved'
        return await extract_files(user_id, files, conn, temp_dir, save_dir)


@user_urls.post("/upload_extracted_records/")
async def upload_after_checking(user_id: str, records: List[UploadRecord]):
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(Worker.worker_id == user_id)
        if query.first() is None:
            return {'msg': '当前账户非法，无法上传'}
    record_dict_list = [record for record in records]
    return await upload_extracted_records(record_dict_list)


@user_urls.post("/search_service/")
async def search_service(user_id: str, search_info: SearchServiceInfo):
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(Worker.worker_id == user_id)
        if query.first() is None:
            return {'msg': '当前账户非法，禁止查询'}
        return await search_service_for_user(user_id, conn, search_info)


@user_urls.post("/search_quota/")
async def search_quota_user(user_id: str, search_info: Union[SearchQuotaInfo, None] = None) -> List[Dict] | Dict:
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(get_where_conditions(Worker.__table__))
        if query.first() is None:
            return {'msg': '当前账户非法，禁止查询'}
        if search_info is None:
            result_list = []
            time_conditions = [SearchQuotaInfo(
                service_time=(datetime(datetime.now().year, 1, 1), datetime(datetime.now().year, 12, 31)))]
            start_date, end_date = await get_season()
            time_conditions.append(SearchQuotaInfo(service_time=(start_date, end_date)))
            time_conditions.append(
                SearchQuotaInfo(service_time=(datetime(datetime.now().year, datetime.now().month, 1),
                                              datetime(datetime.now().year, datetime.now().month,
                                              calendar.monthrange(datetime.now().year, datetime.now().month)[1]))))
            for time_condition in time_conditions:
                result_list.append(await search_quota_for_user(user_id, conn, time_condition))
            return result_list
        else:
            return [await search_quota_for_user(user_id, conn, search_info)]
