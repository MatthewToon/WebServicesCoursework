from pydantic import BaseModel
from app.schemas.catalogue import PageMeta

class PublisherOut(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True  # pydantic v2 ORM mode

class PublisherListOut(BaseModel):
    items: list[PublisherOut]
    meta: PageMeta