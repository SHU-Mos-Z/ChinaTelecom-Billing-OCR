from fastapi import APIRouter, File
from Tools.UploadTools import *
from Tools.SearchTools import *
from Tools.DataBaseTools import *

user_urls = APIRouter()


@user_urls.post("/upload_files/")
async def upload_pdfs_ofds_photos(user_id: str, files: List[UploadFile] = File(...)):
    with Session(bind=engine) as conn:
        query = conn.query(Worker.worker_id).where(Worker.worker_id == user_id)
        if query.first() is None:
            return {'msg': '当前账户非法，无法上传'}
        temp_dir = './uploaded_files/temp'
        save_dir = './uploaded_files/saved'
        return await upload_files(user_id, files, conn, temp_dir, save_dir)


@user_urls.post("/search_service/")
def search_service(user_id: str, search_info: SearchServiceInfo):
    with Session(bind=engine) as conn:
        query = conn.query(ServiceRecord.service_record_id, ServiceRecord.invoice_type,
                           ServiceRecord.service_time, ServiceRecord.service_name, ServiceRecord.cost,
                           ServiceRecord.total, ServiceRecord.total_tax, Worker.worker_name,
                           ServiceRecord.buyer_company, ServiceRecord.seller_company).join(
                           Worker, Worker.worker_id == ServiceRecord.worker_id)
        if user_id is not None:
            query = query.filter(ServiceRecord.worker_id == user_id)
        if search_info.service_name is not None:
            query = query.filter(ServiceRecord.service_name == search_info.service_name)
        if search_info.service_money is not None:
            query = query.filter(ServiceRecord.total.between(search_info.service_money[0], search_info.service_money[1]))
        if search_info.seller_company is not None:
            query = query.filter(
                or_(ServiceRecord.seller_company == search_info.seller_company, ServiceRecord.seller_company is None))
        if search_info.service_time is not None:
            query = query.filter(
                or_(ServiceRecord.service_time.between(search_info.service_time[0], search_info.service_time[1]),
                    ServiceRecord.service_time is None))
        results = query.all()
        if len(results) == 0:
            results = {'msg': '查找结果为空'}
        return results
