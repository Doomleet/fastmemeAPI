from pydantic import BaseModel


class MemeBase(BaseModel):
    text: str


class MemeCreate(MemeBase):
    image_url: str


class Meme(MemeBase):
    id: int
    image_url: str
