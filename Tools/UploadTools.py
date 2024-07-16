from fastapi import UploadFile
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import insert
from Database.Models import *
from Tools.ExtractPDF import *
from Tools.ExtractOFD import *
from Tools.ExtractPhoto import *
from Tools.DataBaseTools import *
import datetime
import pytz


async def save_file(file: UploadFile, user_id: str, save_dir: str) -> str:
    save_file_location = os.path.join(save_dir, user_id, file.filename)
    os.makedirs(os.path.dirname(save_file_location), exist_ok=True)
    with open(save_file_location, "wb") as buffer:
        buffer.write(await file.read())
    return save_file_location


async def process_file(file: UploadFile, user_id: str, conn: Session, temp_dir: str, save_dir: str) -> Dict:
    save_file_location = await save_file(file, user_id, save_dir)
    if file.filename.endswith('.pdf'):
        invoice_type = 'pdf'
        file_info = process_saved_pdf(file_dir=save_file_location)
    elif file.filename.endswith('.ofd'):
        invoice_type = 'ofd'
        file_info = process_saved_ofd(file_dir=save_file_location, temp_file_folder=temp_dir)
    elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        invoice_type = 'image'
        file_info = process_saved_photo(image_path=save_file_location)
    else:
        return {'msg': '上传文件格式不正确，请使用pdf、ofd或图片文件重试'}
    # print(file_info)
    if not validate_invoice(file_info):
        return {'msg': '文件识别信息不充分，请重试'}
    query = conn.query(Worker.worker_name).where(get_where_conditions([Worker.worker_name], file_info['username']))
    if len(query.all()) == 0:
        return {'msg': '扫描得到的员工姓名不存在，请重试'}
    new_record = {
        'service_record_id': file_info['invoice_id'],
        'service_name': file_info['reimbursement_type'],
        'invoice_type': invoice_type,
        'service_time': file_info['invoice_date'],
        'upload_time': datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S'),
        'buyer_company': file_info['buyer_id'],
        'seller_company': file_info['seller_id'],
        'worker_id': user_id,
        'cost': file_info['cost'],
        'total': file_info['total'],
        'total_tax': file_info['total_tax'],
        'is_exception': None,
    }
    try:
        conn.execute(insert(ServiceRecord).values(new_record))
        conn.commit()
        return {'msg': '上传成功，数据已录入'}
    except Exception as e:
        return {'msg': f'数据库插入错误: {e}'}


async def upload_files(user_id: str, files: List[UploadFile], conn: Session, temp_dir: str, save_dir: str) -> List[
    Dict]:
    msg_list = []
    for file in files:
        msg = await process_file(file, user_id, conn, temp_dir, save_dir)
        msg_list.append({file.filename: msg})
    msg_list.append({'final_msg': '数据上传结束'})
    return msg_list


def validate_invoice(data):
    required_keys = ['invoice_id', 'invoice_date', 'buyer_id', 'seller_id', 'username', 'reimbursement_type', 'cost',
                     'total', 'total_tax']
    for key in required_keys:
        if key not in data or data[key] is None or data[key] == '':
            return False
    try:
        total = float(data['total'])
        total_tax = float(data['total_tax'])
        if total_tax <= total:
            return False
    except ValueError:
        return False
    return True
