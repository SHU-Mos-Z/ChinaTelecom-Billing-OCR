from fastapi import APIRouter
from Tools.SearchTools import *
import calendar

group_urls = APIRouter()


# @group_urls.post("/upload_files/")
# async def upload_pdfs_ofds_photos(user_id: str, files: List[UploadFile] = File(...)):
#     with Session(bind=engine) as conn:
#         query = conn.query(Worker.worker_id).where(Worker.worker_id == user_id)
#         if query.first() is None:
#             return {'msg': '当前账户非法，无法上传'}
#         temp_dir = './uploaded_files/temp'
#         save_dir = './uploaded_files/saved'
#         return await extract_and_upload_files(user_id, files, conn, temp_dir, save_dir)


@group_urls.post("/search_quota/", summary='将RequestBody设为null，来获取班组管理页面上方的三条额度显示')
async def search_quota(user_id: str, search_info: Union[SearchTimeZone, None] = None) -> List[Dict] | Dict:
    with Session(bind=engine) as conn:
        query = conn.query(Worker.class_id).filter(Worker.worker_id == user_id).filter(
            Worker.role == 'class_manager')
        if query.first() is None:
            return {'msg': '当前账户非法或者权限不匹配，禁止查询'}
        class_id = query.all()[-1][-1]
        if search_info is None:
            result_list = []
            time_conditions = [SearchTimeZone(
                service_time=(datetime(datetime.now().year, 1, 1), datetime(datetime.now().year, 12, 31)),
                upload_time=None)]
            start_date, end_date = await get_season_now()
            time_conditions.append(SearchTimeZone(service_time=(start_date, end_date), upload_time=None))
            time_conditions.append(
                SearchTimeZone(service_time=(datetime(datetime.now().year, datetime.now().month, 1),
                                             datetime(datetime.now().year, datetime.now().month,
                                                      calendar.monthrange(datetime.now().year,
                                                                          datetime.now().month)[1])), upload_time=None))
            for time_condition in time_conditions:
                result_list.append(await search_quota_for_class(class_id, conn, time_condition))
            return result_list
        else:
            return [await search_quota_for_class(class_id, conn, search_info)]


@group_urls.post("/search_service/", summary='根据登录的班组管理员所在班组，给出班组所有员工的表格信息')
async def search_service(user_id: str, search_info: Union[SearchTimeZone, None] = None) -> List[Dict] | Dict:
    with Session(bind=engine) as conn:
        query = conn.query(Worker.class_id).filter(Worker.worker_id == user_id).filter(
            Worker.role == 'class_manager')
        if query.first() is None:
            return {'msg': '当前账户非法或者权限不匹配，禁止查询'}
        class_id = query.all()[-1][-1]
        return await search_service_for_class(class_id, conn, search_info)
