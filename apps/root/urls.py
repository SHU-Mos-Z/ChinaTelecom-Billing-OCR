import datetime
from Tools.UploadTools import *
from fastapi import APIRouter, File
from Tools.SearchTools import *
# from fastapi import Depends
# from fastapi_limiter.depends import RateLimiter

root_urls = APIRouter()


@root_urls.post("/upload_files/")
async def upload_pdfs_ofds_photos(user_id: str, files: List[UploadFile] = File(...)):
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(
            get_where_conditions([Worker.worker_id, Worker.role], user_id, 'system_manager'))
        if query.first() is None:
            return {'msg': '当前账户非法或者权限过低，禁止查询'}
        temp_dir = './uploaded_files/temp'
        save_dir = './uploaded_files/saved'
        return await extract_and_upload_files(user_id, files, conn, temp_dir, save_dir)


@root_urls.post("/search_quota_all/")
async def search_quota_all(user_id: str, target_year: str = None) -> Dict:
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(
            get_where_conditions([Worker.worker_id, Worker.role], user_id, 'system_manager'))
        if query.first() is None:
            return {'msg': '当前账户非法或者权限过低，禁止查询'}
        query = conn.query(Clas.class_id)
        class_id_list = [tup[0] for tup in query.all()]
        result_dict = dict()
        for class_id in class_id_list:
            result_class = []
            class_total = dict()
            for month in ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec'):
                class_total[month] = 0.0
            worker_id_name_class = conn.query(
                Worker.worker_id, Worker.worker_name).where(Worker.class_id == class_id)
            for worker_id, worker_name in zip([tup[0] for tup in worker_id_name_class],
                                              [tup[1] for tup in worker_id_name_class]):
                result_user = {'worker_id': worker_id, 'worker_name': worker_name}
                if target_year is None:
                    target_year = datetime.now().year
                worker_quota = conn.query(WorkerQuotaMonthly.quota_01, WorkerQuotaMonthly.quota_02,
                                          WorkerQuotaMonthly.quota_03, WorkerQuotaMonthly.quota_04,
                                          WorkerQuotaMonthly.quota_05, WorkerQuotaMonthly.quota_06,
                                          WorkerQuotaMonthly.quota_07, WorkerQuotaMonthly.quota_08,
                                          WorkerQuotaMonthly.quota_09, WorkerQuotaMonthly.quota_10,
                                          WorkerQuotaMonthly.quota_11, WorkerQuotaMonthly.quota_12).where(
                    get_where_conditions([WorkerQuotaMonthly.worker_id, WorkerQuotaMonthly.year_],
                                         worker_id, target_year))
                for month, quota in zip(('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
                                         'aug', 'sept', 'oct', 'nov', 'dec'), worker_quota[0]):
                    result_user[month] = quota
                    class_total[month] += quota
                result_class.append(result_user)
            result_class.append(class_total)
            result_dict[class_id] = result_class
        return result_dict
