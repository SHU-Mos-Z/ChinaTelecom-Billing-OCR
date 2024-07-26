from io import BytesIO
from random import randint, sample
from string import ascii_letters, digits
from typing import Tuple, Annotated
from PIL.Image import new
from PIL.ImageDraw import Draw
from PIL.ImageFilter import EDGE_ENHANCE_MORE
from PIL.ImageFont import truetype
from fastapi import APIRouter
# from typing import Annotated
# from sqlalchemy.orm import Session
from Database.Models import *
from Tools.DataBaseTools import *
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

login_urls = APIRouter()
encryption_key = open('./apps/login/pwd.key', 'rb').read()
SECRET_KEY = "23e8d339bdc8d8589a51a788fd1bb95f2113fd6950abab9ae576cc62fdf63e18"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")


class CheckCode(object):
    def __init__(
            self,
            image_width: int = 150,
            image_height: int = 40,
            character_length: int = 4,
            font_size: int = 30,
            mode: str = 'RGB',
            color: Tuple[int] = (255, 255, 255),
            font_file: str = 'apps/login/DejaVuSansMono-Bold.ttf',
    ) -> None:
        self.image_width = image_width
        self.image_height = image_height
        self.character_length = character_length
        self.image = new(mode=mode, size=(image_width, image_height), color=color)
        self.draw = Draw(im=self.image, mode=mode)
        self.create_font = truetype(font=font_file, size=font_size)
        self.random_characters = sample(ascii_letters + digits, self.character_length)

    # 开始创建
    async def create_check_code(self):
        for _index, _character in enumerate(self.random_characters):
            font_start_height = randint(-4, 4)
            self.draw.text(
                xy=(_index * self.image_width / self.character_length, font_start_height),
                text=_character,
                font=self.create_font,
                fill=await random_color()
            )

        for _ in range(150):
            self.draw.point([randint(0, self.image_width),
                             randint(0, self.image_height)],
                            fill=await random_color())

            self.draw.point([randint(0, self.image_width),
                             randint(0, self.image_height)],
                            fill=await random_color())
            x = randint(0, self.image_width)
            y = randint(0, self.image_height)
            radius = randint(2, 4)
            self.draw.arc(xy=(x - radius, y - radius, x + radius, y + radius),
                          start=0,
                          end=90,
                          fill=await random_color())

        for _ in range(10):
            x1 = randint(0, self.image_width)
            y1 = randint(0, self.image_height)
            x2 = randint(0, self.image_width)
            y2 = randint(0, self.image_height)
            self.draw.line((x1, y1, x2, y2), fill=await random_color())

        self.image.filter(EDGE_ENHANCE_MORE)
        image_io = BytesIO()
        self.image.save(image_io, 'png')
        self.image.close()
        image_io.seek(0)
        return image_io, ''.join(self.random_characters).lower()


async def random_color():
    return randint(150, 235), randint(150, 235), randint(150, 235)


class User(BaseModel):
    worker_id: str
    worker_name: str
    role: str
    pwd: str


class Token(BaseModel):
    access_token: str
    token_type: str


# return的worker可能为空
async def get_pydantic_user_from_db(user_id: str):
    with Session(bind=engine) as conn:
        worker_query = conn.query(Worker.worker_id, Worker.worker_name, Worker.role, Worker.pwd).filter(
            Worker.worker_id == user_id)
    if len(worker_query.all()) == 0:
        return None
    else:
        return User(worker_id=worker_query.first()[0], worker_name=worker_query.first()[1],
                    role=worker_query.first()[2], pwd=worker_query.first()[3])


async def verify_password(plain_password, hashed_password):
    print(
        f"用户输入的密码：{plain_password}, 加密后：{encrypt_string(plain_password, encryption_key)}, 数据库中的密码：{hashed_password}")
    print(
        f"用户输入的密码：{plain_password}, 数据库中的密码：{hashed_password}，解密后：{decrypt_string(hashed_password, encryption_key)}")
    if decrypt_string(hashed_password, encryption_key) == plain_password:
        return True
    return False


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception as _:
        raise credentials_exception
    user = await get_pydantic_user_from_db(user_id=user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_group_user(current_user: User = Depends(get_current_user)):
    if current_user.role != 'group_manager':
        raise HTTPException(status_code=400, detail="Not group manager")
    return current_user


async def get_current_center_user(current_user: User = Depends(get_current_user)):
    if current_user.role != 'center_manager':
        raise HTTPException(status_code=400, detail="Not center manager")
    return current_user


async def get_current_system_user(current_user: User = Depends(get_current_user)):
    if current_user.role != 'system_manager':
        raise HTTPException(status_code=400, detail="Not system manager")
    return current_user
