from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    price: float
    in_stock: bool = True


class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    in_stock: bool | None = None


class ItemResponse(BaseModel):
    item_id: int
    item: ItemCreate
