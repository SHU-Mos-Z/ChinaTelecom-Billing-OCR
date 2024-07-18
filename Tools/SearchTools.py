from typing import Union, Tuple, Dict
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from Database.Models import *


class SearchServiceInfo(BaseModel):
    service_name: Union[str, None] = None
    service_money: Union[Tuple[float, float], None] = None
    seller_company: Union[str, None] = None
    service_time: Union[Tuple[datetime, datetime], None] = (
        datetime(datetime.now().year, 1, 1),
        datetime(datetime.now().year, 12, 31, 23, 59, 59)
    )
    is_exception: Union[bool, None] = False


class SearchQuotaInfo(BaseModel):
    service_time: Union[Tuple[datetime, datetime], None] = (
        datetime(datetime.now().year, 1, 1),
        datetime(datetime.now().year, 12, 31)
    )


async def search_quota_for_user(user_id: str, conn: Session, search_info: SearchQuotaInfo) -> Dict:
    query = conn.query(WorkerQuotaMonthly.quota_01, WorkerQuotaMonthly.quota_02, WorkerQuotaMonthly.quota_03,
                       WorkerQuotaMonthly.quota_04, WorkerQuotaMonthly.quota_05, WorkerQuotaMonthly.quota_06,
                       WorkerQuotaMonthly.quota_07, WorkerQuotaMonthly.quota_08, WorkerQuotaMonthly.quota_09,
                       WorkerQuotaMonthly.quota_10, WorkerQuotaMonthly.quota_11, WorkerQuotaMonthly.quota_12)
    if user_id is not None:
        query = query.filter(WorkerQuotaMonthly.worker_id == user_id)
    if search_info.service_time is not None:
        query = query.filter(
            WorkerQuotaMonthly.year_.between(search_info.service_time[0], search_info.service_time[1]))
    year = int(search_info.service_time[0].year)
    idx = 0
    quota_sum = 0.0
    if search_info.service_time[0].year == search_info.service_time[1].year:
        quota_sum += sum(
            query.all()[idx][int(search_info.service_time[0].month) - 1:int(search_info.service_time[1].month)])
    else:
        while year <= int(search_info.service_time[1].year):
            if year != search_info.service_time[0].year and year != search_info.service_time[1].year:
                quota_sum += sum(query.all()[idx])
            else:
                if year == search_info.service_time[0].year:
                    quota_sum += sum(query.all()[idx][int(search_info.service_time[0].month) - 1:])
                else:
                    quota_sum += sum(query.all()[idx][:int(search_info.service_time[1].month)])
            year += 1
            idx += 1
    query = conn.query(ServiceRecord.total_tax)
    if user_id is not None:
        query = query.filter(ServiceRecord.worker_id == user_id)
    if search_info.service_time is not None:
        query = query.filter(
            ServiceRecord.service_time.between(search_info.service_time[0], search_info.service_time[1]))
    quota_used = 0.0
    for tup in query.all():
        quota_used += tup[0]
    return {'start_time': search_info.service_time[0], 'end_time': search_info.service_time[1], 'quota': quota_sum,
            'used_quota': quota_used}


async def get_season():
    now = datetime.now()
    if 1 <= now.month <= 3:
        start_date = datetime(now.year, 1, 1)
        end_date = datetime(now.year, 3, 31)
    elif 4 <= now.month <= 6:
        start_date = datetime(now.year, 4, 1)
        end_date = datetime(now.year, 6, 30)
    elif 7 <= now.month <= 9:
        start_date = datetime(now.year, 7, 1)
        end_date = datetime(now.year, 9, 30)
    else:
        start_date = datetime(now.year, 10, 1)
        end_date = datetime(now.year, 12, 31)
    return start_date, end_date
