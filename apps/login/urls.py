from Tools.Login import *
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm


@login_urls.get('/get_code', summary='login code')
async def get_code():
    _image, _code = await CheckCode().create_check_code()
    return StreamingResponse(content=_image, media_type="image/png", headers={"code": _code})


@login_urls.post('/token', summary='user login')
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_id = form_data.username
    password = form_data.password
    worker = await get_pydantic_user_from_db(user_id)
    # 若数据库中没有这个用户
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 如果有这个用户，但是密码不正确
    if not await verify_password(password, worker.pwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 用户名密码正确，返回一个 一定有效期内的token，用于后续的身份验证
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": worker.worker_id}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# @login_urls.get("/users/me/", response_model=User)
# async def read_users_me(current_user: Annotated[Worker, Depends(get_current_user)]):
#     pass
#
#
# @login_urls.get("/users/me/group/", response_model=User)
# async def read_own_items(current_user: Annotated[Worker, Depends(get_current_group_user)]):
#     pass


# @login_urls.get('/user/normal_login', summary='user login')
# def user_login(user_id: Union[str, None] = None, pwd: Union[str, None] = None):
#     if user_id is None or pwd is None:
#         return {'msg': '未请输入用户名或密码'}
#     with Session(bind=engine) as conn:
#         query = conn.query(Worker.pwd).where(get_where_conditions(Worker.__table__.columns.values(), user_id))
#         if len(query.all()) == 0:
#             return {'msg': '用户不存在'}
#         check_str = decrypt_string(query.all()[0][0], encryption_key)
#         if str(check_str) == pwd:
#             return {'msg': '密码正确，允许登录'}
#         else:
#             return {'msg': '密码错误，请重试'}
#
#
# @login_urls.get('/user/group_login', summary='group manager login')
# def group_login(user_id: Union[str, None] = None, pwd: Union[str, None] = None):
#     if user_id is None or pwd is None:
#         return {'msg': '未请输入用户名或密码'}
#     with Session(bind=engine) as conn:
#         query = conn.query(Worker.pwd, Worker.role).where(
#             get_where_conditions(Worker.__table__.columns.values(), user_id))
#         if len(query.all()) == 0:
#             return {'msg': '用户不存在'}
#         elif query.all()[0][1] == 'normal' or query.all()[0][1] == 'super':
#             return {'msg': '用户权限不匹配'}
#         check_str = decrypt_string(query.all()[0][0], encryption_key)
#         if str(check_str) == pwd:
#             return {'msg': '密码正确，允许登录'}
#         else:
#             return {'msg': '密码错误，请重试'}
#
#
# @login_urls.get('/user/super_login', summary='super manager login')
# def group_login(user_id: Union[str, None] = None, pwd: Union[str, None] = None):
#     if user_id is None or pwd is None:
#         return {'msg': '未请输入用户名或密码'}
#     with Session(bind=engine) as conn:
#         query = conn.query(Worker.pwd, Worker.role).where(
#             get_where_conditions(Worker.__table__.columns.values(), user_id))
#         if len(query.all()) == 0:
#             return {'msg': '用户不存在'}
#         elif query.all()[0][1] == 'normal' or query.all()[0][1] == 'group':
#             return {'msg': '登录账号权限不匹配'}
#         check_str = decrypt_string(query.all()[0][0], encryption_key)
#         if str(check_str) == pwd:
#             return {'msg': '密码正确，允许登录'}
#         else:
#             return {'msg': '密码错误，请重试'}
