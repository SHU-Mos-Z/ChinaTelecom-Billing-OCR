from fastapi import APIRouter
from typing import Union
from sqlalchemy.orm import Session
from Database.Models import *
from Tools.DataBaseTools import *
from Tools.LoginCode import *
from fastapi.responses import StreamingResponse

login_urls = APIRouter()
encryption_key = open('./apps/login/pwd.key', 'rb').read()


@login_urls.get('/user/get_code', summary='login code')
async def get_code():
    _image, _code = await CheckCode().create_check_code()
    return StreamingResponse(content=_image, media_type="image/png", headers={"code": _code})


@login_urls.get('/user/normal_login', summary='user login')
def user_login(user_id: Union[str, None] = None, pwd: Union[str, None] = None):
    if user_id is None or pwd is None:
        return {'msg': '未请输入用户名或密码'}
    with Session(bind=engine) as conn:
        query = conn.query(Worker.pwd).where(get_where_conditions(Worker.__table__.columns.values(), user_id))
        if len(query.all()) == 0:
            return {'msg': '用户不存在'}
        check_str = decrypt_string(query.all()[0][0], encryption_key)
        if str(check_str) == pwd:
            return {'msg': '密码正确，允许登录'}
        else:
            return {'msg': '密码错误，请重试'}


@login_urls.get('/user/group_login', summary='group manager login')
def group_login(user_id: Union[str, None] = None, pwd: Union[str, None] = None):
    if user_id is None or pwd is None:
        return {'msg': '未请输入用户名或密码'}
    with Session(bind=engine) as conn:
        query = conn.query(Worker.pwd, Worker.role).where(
            get_where_conditions(Worker.__table__.columns.values(), user_id))
        if len(query.all()) == 0:
            return {'msg': '用户不存在'}
        elif query.all()[0][1] == 'normal' or query.all()[0][1] == 'super':
            return {'msg': '用户权限不匹配'}
        check_str = decrypt_string(query.all()[0][0], encryption_key)
        if str(check_str) == pwd:
            return {'msg': '密码正确，允许登录'}
        else:
            return {'msg': '密码错误，请重试'}


@login_urls.get('/user/super_login', summary='super manager login')
def group_login(user_id: Union[str, None] = None, pwd: Union[str, None] = None):
    if user_id is None or pwd is None:
        return {'msg': '未请输入用户名或密码'}
    with Session(bind=engine) as conn:
        query = conn.query(Worker.pwd, Worker.role).where(
            get_where_conditions(Worker.__table__.columns.values(), user_id))
        if len(query.all()) == 0:
            return {'msg': '用户不存在'}
        elif query.all()[0][1] == 'normal' or query.all()[0][1] == 'group':
            return {'msg': '登录账号权限不匹配'}
        check_str = decrypt_string(query.all()[0][0], encryption_key)
        if str(check_str) == pwd:
            return {'msg': '密码正确，允许登录'}
        else:
            return {'msg': '密码错误，请重试'}
