from pydantic import BaseModel
from app.schemas.catalogue import PageMeta

class GameOut(BaseModel):
    id: int
    name: str
    year: int | None

    na_sales: float
    eu_sales: float
    jp_sales: float
    other_sales: float
    global_sales: float

    publisher_id: int
    platform_id: int
    genre_id: int

    class Config:
        from_attributes = True

class GameListOut(BaseModel):
    items: list[GameOut]
    meta: PageMeta