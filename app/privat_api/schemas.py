from pydantic import BaseModel


class DeleteMemeRequest(BaseModel):
    url: str
