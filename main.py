from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from apps.user.urls import user_urls
from apps.login.urls import login_urls
from apps.group.urls import group_urls
from apps.root.urls import root_urls
from apps.center.urls import center_urls
import uvicorn
from Tools.InitPwd import *

app = FastAPI()

# @app.on_event("startup")
# async def startup():
#     redis = await aioredis.create_redis_pool("redis://localhost")
#     await FastAPILimiter.init(redis)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(user_urls, prefix='/user', tags=['api for worker users'])
app.include_router(group_urls, prefix='/group', tags=['api for group manager users'])
app.include_router(center_urls, prefix='/center', tags=['api for center manager users'])
app.include_router(root_urls, prefix='/root', tags=['api for system users'])
app.include_router(login_urls, prefix='/login', tags=['api for login'])

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)
