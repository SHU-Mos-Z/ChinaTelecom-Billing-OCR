from typing import Union, Dict, List
from sqlalchemy import or_
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from Database.Models import *
from Tools.DataBaseTools import *


class SearchServiceInfoUser(BaseModel):
    service_name: Union[str, None] = None
    service_money: Union[List[float | None], None] = None
    seller_company_id: Union[str, None] = None
    service_time: Union[List[datetime | None], None] = [
        datetime(datetime.now().year, 1, 1),
        datetime(datetime.now().year, 12, 31, 23, 59, 59)
    ]
    upload_time: Union[List[datetime | None], None] = [
        datetime(datetime.now().year, 1, 1),
        datetime(datetime.now().year, 12, 31, 23, 59, 59)
    ]
    is_exception: Union[bool, None] = False


class SearchTimeZone(BaseModel):
    service_time: Union[List[datetime | None], None] = [
        datetime(datetime.now().year, 1, 1),
        datetime(datetime.now().year, 12, 31)
    ]
    upload_time: Union[List[datetime | None], None] = [
        datetime(datetime.now().year, 1, 1),
        datetime(datetime.now().year, 12, 31)
    ]


class SearchServiceInfoRoot(BaseModel):
    service_time: Union[List[datetime | None], None] = [
        datetime(datetime.now().year, 1, 1),
        datetime(datetime.now().year, 12, 31)
    ]
    year: Union[int, None] = None
    season: Union[int, None] = None


async def search_service_for_user(user_id: str, conn: Session, search_info: SearchServiceInfoUser):
    query = conn.query(ServiceRecord.service_record_id, ServiceRecord.invoice_type,
                       ServiceRecord.service_time, ServiceRecord.service_name, ServiceRecord.cost,
                       ServiceRecord.total, ServiceRecord.total_tax, Worker.worker_name,
                       ServiceRecord.buyer_company_id, ServiceRecord.seller_company_id,
                       ServiceRecord.buyer_company_name, ServiceRecord.seller_company_name).join(
        Worker, Worker.worker_id == ServiceRecord.worker_id)
    if user_id is not None:
        query = query.filter(ServiceRecord.worker_id == user_id)
    if search_info.service_name is not None:
        query = query.filter(ServiceRecord.service_name == search_info.service_name)
    if search_info.service_money is not None:
        if search_info.service_money[0] is None:
            search_info.service_money[0] = 0.0
        if search_info.service_money[1] is None:
            search_info.service_money[1] = 99999999.9
        query = query.filter(
            ServiceRecord.total.between(search_info.service_money[0], search_info.service_money[1]))
    if search_info.seller_company_id is not None:
        query = query.filter(
            or_(ServiceRecord.seller_company_id == search_info.seller_company_id,
                ServiceRecord.seller_company_id is None))
    search_info = await cover_time_zone(conn, search_info)
    query = query.filter(
        or_(ServiceRecord.upload_time.between(search_info.upload_time[0], search_info.upload_time[1]),
            ServiceRecord.upload_time is None))
    if search_info.is_exception is not None:
        query = query.filter(
            or_(ServiceRecord.is_exception == search_info.is_exception, ServiceRecord.is_exception is None))
    results = query.all()
    if len(results) == 0:
        results = {'msg': '查找结果为空'}
    return results


async def search_quota_for_user(user_id: str, conn: Session, search_info: SearchTimeZone) -> Dict:
    query = conn.query(WorkerQuotaMonthly.quota_01, WorkerQuotaMonthly.quota_02, WorkerQuotaMonthly.quota_03,
                       WorkerQuotaMonthly.quota_04, WorkerQuotaMonthly.quota_05, WorkerQuotaMonthly.quota_06,
                       WorkerQuotaMonthly.quota_07, WorkerQuotaMonthly.quota_08, WorkerQuotaMonthly.quota_09,
                       WorkerQuotaMonthly.quota_10, WorkerQuotaMonthly.quota_11, WorkerQuotaMonthly.quota_12)
    if user_id is not None:
        query = query.filter(WorkerQuotaMonthly.worker_id == user_id)
    search_info = await cover_time_zone(conn, search_info)
    query = query.filter(WorkerQuotaMonthly.year_.between(search_info.service_time[0], search_info.service_time[1]))
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


async def get_season_now():
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


async def get_season(year: int, season_idx: int):
    if season_idx == 1:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 3, 31)
    elif season_idx == 2:
        start_date = datetime(year, 4, 1)
        end_date = datetime(year, 6, 30)
    elif season_idx == 3:
        start_date = datetime(year, 7, 1)
        end_date = datetime(year, 9, 30)
    else:
        start_date = datetime(year, 10, 1)
        end_date = datetime(year, 12, 31)
    return start_date, end_date


async def search_all_worker_for_root(conn: Session):
    query = conn.query(Clas.class_id)
    class_id_list = [tup[0] for tup in query.all()]
    result_dict = dict()
    for class_id in class_id_list:
        result_class = []
        query = conn.query(Worker.worker_id, Worker.worker_name, Worker.role).where(
            get_where_conditions([Worker.class_id], class_id))
        for tup in query.all():
            result_class.append(dict((k, v) for k, v in zip(['worker_id', 'worker_name', 'role'], tup)))
        result_dict[class_id] = result_class
    return result_dict


async def search_quota_for_root(conn: Session, target_year: str = None):
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


async def search_service_year_season_for_root(conn: Session, search_info: SearchServiceInfoRoot):
    query = conn.query(ServiceRecord.total_tax, ServiceRecord.service_time, ServiceRecord.upload_time,
                       ServiceRecord.service_record_id, ServiceRecord.invoice_type, ServiceRecord.service_name,
                       ServiceRecord.cost, ServiceRecord.total, Worker.worker_name, ServiceRecord.buyer_company_name,
                       ServiceRecord.buyer_company_id, ServiceRecord.seller_company_name,
                       ServiceRecord.seller_company_id).join(Worker, Worker.worker_id == ServiceRecord.worker_id)
    min_year, _ = await get_min_max_year(conn)
    if search_info.year is None or search_info.year < min_year:
        search_info.year = datetime.now().year
    if search_info.year <= min_year:
        search_info.year = min_year
    if search_info.season is None or search_info.season <= 1:
        search_info.season = 1
    if search_info.season >= 4:
        search_info.season = 4
    _, end = await get_season(search_info.year, search_info.season)
    query = query.filter(
        ServiceRecord.service_time.between(datetime(search_info.year, 1, 1), end))
    min_year, max_year = await get_min_max_year(conn)
    if search_info.service_time is not None:
        if search_info.service_time[0] is None:
            search_info.service_time[0] = datetime(min_year, 1, 1)
        if search_info.service_time[1] is None:
            search_info.service_time[1] = datetime(max_year, 12, 31)
        start = search_info.service_time[0]
        end = search_info.service_time[1]
        if search_info.service_time[0].year != search_info.year:
            start = datetime(search_info.year, search_info.service_time[0].month, search_info.service_time[0].day)
        if search_info.service_time[1].year != search_info.year:
            end = datetime(search_info.year, search_info.service_time[1].month, search_info.service_time[1].day)
        query = query.filter(
            ServiceRecord.service_time.between(start, end))
    result_dict_list = []
    dict_key_list = [
        "total_tax", "service_time", "upload_time", "service_record_id", "invoice_type", "service_name",
        "cost", "total", "worker_name", "buyer_company_name", "buyer_company_id", "seller_company_name",
        "seller_company_id"]
    for tup in query.all():
        result_dict_list.append(dict((k, v) for k, v in zip(dict_key_list, tup)))
    return result_dict_list


async def search_quota_class_for_center(conn: Session, search_info: SearchTimeZone):
    class_id_list = [tup[0] for tup in conn.query(Clas.class_id).all()]
    result_dict_list = []
    for class_id in class_id_list:
        query = conn.query(ServiceRecord.total_tax, ServiceRecord.is_exception, Clas.class_name).join(
            Worker, Worker.worker_id == ServiceRecord.worker_id).join(Clas, Clas.class_id == Worker.class_id)
        query = query.filter(Clas.class_id == class_id)
        query_quota = conn.query(ClassQuotaMonthly.quota_01, ClassQuotaMonthly.quota_02, ClassQuotaMonthly.quota_03,
                                 ClassQuotaMonthly.quota_04, ClassQuotaMonthly.quota_05, ClassQuotaMonthly.quota_06,
                                 ClassQuotaMonthly.quota_07, ClassQuotaMonthly.quota_08, ClassQuotaMonthly.quota_09,
                                 ClassQuotaMonthly.quota_10, ClassQuotaMonthly.quota_11,
                                 ClassQuotaMonthly.quota_12).filter(ClassQuotaMonthly.class_id == class_id)
        search_info = await cover_time_zone(conn, search_info)
        query = query.filter(
            ServiceRecord.upload_time.between(search_info.upload_time[0], search_info.upload_time[1])).filter(
            ServiceRecord.service_time.between(search_info.service_time[0], search_info.service_time[1])
        )
        query_quota = query_quota.filter(
            ClassQuotaMonthly.year_.between(search_info.upload_time[0].year, search_info.upload_time[1].year)).filter(
            ClassQuotaMonthly.year_.between(search_info.service_time[0].year, search_info.service_time[1].year)
        )
        if len(query.all()) == 0 or len(query_quota.all()) == 0:
            class_name = conn.query(Clas.class_name).filter(Clas.class_id == class_id).all()[0][0]
            result_dict_list.append({'class_name': class_name, 'total_tax': 0.0, 'num_invoice': 0,
                                     'num_invoice_exception': 0.0, 'quota': 0.0})
            continue
        key_list = ['class_name', 'total_tax', 'num_invoice', 'num_invoice_exception', 'quota']
        value_list = [query.all()[0][2], sum([tup[0] for tup in query.all()]), len(query.all()),
                      sum([tup[1] for tup in query.all()]), 0.0]
        result_dict = dict((k, v) for k, v in zip(key_list, value_list))
        for i, tup in enumerate(query_quota.all()):
            if 0 < i < len(query_quota.all()) - 1:
                result_dict['quota'] += sum(tup)
            elif i == 0:
                if len(query.all()) == 1:
                    result_dict['quota'] += sum(tup[max(search_info.service_time[0].month,
                                                        search_info.upload_time[0].month) - 1:min(
                        search_info.service_time[1].month, search_info.upload_time[1].month)])
                else:
                    result_dict['quota'] += sum(tup[max(search_info.service_time[0].month,
                                                        search_info.upload_time[0].month) - 1:])
            else:
                if len(query.all()) == 1:
                    result_dict['quota'] += sum(tup[max(search_info.service_time[0].month,
                                                        search_info.upload_time[0].month) - 1:min(
                        search_info.service_time[1].month, search_info.upload_time[1].month)])
                else:
                    result_dict['quota'] += sum(tup[:min(search_info.service_time[1].month,
                                                         search_info.upload_time[1].month)])
        result_dict_list.append(result_dict)
    return result_dict_list


async def search_quota_for_class(class_id: str, conn: Session, search_info: SearchTimeZone) -> Dict:
    query = conn.query(ClassQuotaMonthly.quota_01, ClassQuotaMonthly.quota_02, ClassQuotaMonthly.quota_03,
                       ClassQuotaMonthly.quota_04, ClassQuotaMonthly.quota_05, ClassQuotaMonthly.quota_06,
                       ClassQuotaMonthly.quota_07, ClassQuotaMonthly.quota_08, ClassQuotaMonthly.quota_09,
                       ClassQuotaMonthly.quota_10, ClassQuotaMonthly.quota_11, ClassQuotaMonthly.quota_12)
    if class_id is not None:
        query = query.filter(ClassQuotaMonthly.class_id == class_id)
    search_info = await cover_time_zone(conn, search_info)
    query = query.filter(
        ClassQuotaMonthly.year_.between(search_info.service_time[0].year, search_info.service_time[1].year))
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
    query = conn.query(ServiceRecord.total_tax).join(Worker, Worker.worker_id == ServiceRecord.worker_id).join(
        Clas, Clas.class_id == Worker.class_id)
    query = query.filter(Clas.class_id == class_id).filter(
        ServiceRecord.service_time.between(search_info.service_time[0], search_info.service_time[1]))
    quota_used = 0.0
    for tup in query.all():
        quota_used += tup[0]
    return {'start_time': search_info.service_time[0], 'end_time': search_info.service_time[1], 'quota': quota_sum,
            'used_quota': quota_used}


async def search_service_for_class(class_id: str, conn: Session, search_info: SearchTimeZone):
    query_worker = conn.query(Worker.worker_id, Worker.worker_name).filter(Worker.class_id == class_id)
    worker_id_list = [tup[0] for tup in query_worker.all()]
    worker_name_list = [tup[1] for tup in query_worker.all()]
    search_info = await cover_time_zone(conn, search_info)
    result_dict_list = []
    for worker_id, worker_name in zip(worker_id_list, worker_name_list):
        result_dict = dict()
        result_dict['worker_name'] = worker_name
        query = conn.query(ServiceRecord.total_tax, ServiceRecord.is_exception).filter(
            ServiceRecord.worker_id == worker_id).filter(
            ServiceRecord.upload_time.between(search_info.upload_time[0], search_info.upload_time[1])).filter(
            ServiceRecord.service_time.between(search_info.service_time[0], search_info.service_time[1])
        )
        result_dict['total_tax'] = sum([tup[0] for tup in query.all()])
        result_dict['num_exception'] = sum([tup[1] for tup in query.all()])
        result_dict['num_invoice'] = len(query.all())
        query = conn.query(WorkerQuotaMonthly.quota_01, WorkerQuotaMonthly.quota_02,
                           WorkerQuotaMonthly.quota_03, WorkerQuotaMonthly.quota_04,
                           WorkerQuotaMonthly.quota_05, WorkerQuotaMonthly.quota_06,
                           WorkerQuotaMonthly.quota_07, WorkerQuotaMonthly.quota_08,
                           WorkerQuotaMonthly.quota_09, WorkerQuotaMonthly.quota_10,
                           WorkerQuotaMonthly.quota_11, WorkerQuotaMonthly.quota_12).filter(
            WorkerQuotaMonthly.worker_id == worker_id)
        start_year = max(search_info.service_time[0].year, search_info.upload_time[0].year)
        end_year = min(search_info.service_time[1].year, search_info.upload_time[1].year)
        idx = 0
        year = start_year
        result_dict['quota_sum'] = 0.0
        while year <= end_year:
            if start_year == end_year:
                result_dict['quota_sum'] += sum(
                    query.all()[0][max(search_info.service_time[0].month, search_info.upload_time[0].month) - 1: min(
                        search_info.service_time[1].month, search_info.upload_time[1].month)])
            else:
                if start_year < year < end_year:
                    result_dict['quota_sum'] += sum(query.all()[idx])
                elif year == start_year:
                    result_dict['quota_sum'] += sum(
                        query.all()[idx][max(search_info.service_time[0].month, search_info.upload_time[0].month) - 1:])
                else:
                    result_dict['quota_sum'] += sum(
                        query.all()[idx][:min(search_info.service_time[1].month, search_info.upload_time[1].month)])
            year += 1
            idx += 1
        result_dict_list.append(result_dict)
    return result_dict_list


async def get_min_max_year(conn: Session):
    min_year = min([tup[0] for tup in conn.query(ClassQuotaMonthly.year_).all()])
    max_year = max([tup[0] for tup in conn.query(ClassQuotaMonthly.year_).all()])
    return min_year, max_year


async def cover_time_zone(conn: Session, search_info: Union[SearchTimeZone, SearchServiceInfoUser, None]):
    min_year, max_year = await get_min_max_year(conn)
    if search_info is None:
        search_info = SearchTimeZone(service_time=None, upload_time=None)
    if search_info.service_time is None:
        search_info.service_time = [datetime(min_year, 1, 1), datetime(max_year, 12, 31)]
    else:
        if search_info.service_time[0] is None:
            search_info.service_time[0] = datetime(min_year, 1, 1)
        if search_info.service_time[1] is None:
            search_info.service_time[1] = datetime(max_year, 12, 31)
    if search_info.upload_time is None:
        search_info.upload_time = [datetime(min_year, 1, 1), datetime(max_year, 12, 31)]
    else:
        if search_info.upload_time[0] is None:
            search_info.upload_time[0] = datetime(min_year, 1, 1)
        if search_info.upload_time[1] is None:
            search_info.upload_time[1] = datetime(max_year, 12, 31)
    return search_info
