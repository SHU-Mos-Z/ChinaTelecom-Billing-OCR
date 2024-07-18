from sqlalchemy import update
from sqlalchemy.orm import Session
from Database.Models import *
from Tools.DataBaseTools import *

engine = create_engine(url='mysql://root:' + SQL_PWD + '@localhost/ChinaTelecom')

encryption_key = open('./apps/login/pwd.key', 'rb').read()

# 每次服务器开启或自检时，使用用户名初始化密码并加密，方便接口测试
# 如要阻止，需要在main.py中去除相应import语句
with Session(bind=engine) as conn:
    query = conn.query(Worker.worker_id)
    for tup in query.all():
        encrypted_str = encrypt_string(tup[0], encryption_key)
        query = update(Worker).where(get_where_conditions(Worker.__table__.columns.values(), tup[0])).values(
            **get_update_dict(['pwd'], [encrypted_str]))
        try:
            conn.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
