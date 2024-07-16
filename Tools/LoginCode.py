from io import BytesIO
from random import randint, sample
from string import ascii_letters, digits
from typing import Tuple

from PIL.Image import new
from PIL.ImageDraw import Draw
from PIL.ImageFilter import EDGE_ENHANCE_MORE
from PIL.ImageFont import truetype


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
