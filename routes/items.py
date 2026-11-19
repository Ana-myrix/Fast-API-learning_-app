from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.database import get_db
from models.item import Item
from schemas.item import ItemCreate, ItemResponse, ItemUpdate
from services import item_service

router = APIRouter(prefix="/items", tags=["items"])


def _to_response(item: Item) -> dict:
    return {
        "item_id": item.id,
        "item": {"name": item.name, "price": item.price, "in_stock": item.in_stock},
    }


@router.get("/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


# POST - create a new item
@router.post("/{item_id}", status_code=201, response_model=ItemResponse)
def create_item(item_id: int, body: ItemCreate, db: Session = Depends(get_db)):
    item = item_service.create_item(db, item_id, body.model_dump())
    return _to_response(item)


# PUT - replace an existing item completely
@router.put("/{item_id}", response_model=ItemResponse)
def replace_item(item_id: int, body: ItemCreate, db: Session = Depends(get_db)):
    item = item_service.replace_item(db, item_id, body.model_dump())
    return _to_response(item)


# PATCH - update only the fields that were sent
@router.patch("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, body: ItemUpdate, db: Session = Depends(get_db)):
    item = item_service.update_item(db, item_id, body.model_dump(exclude_unset=True))
    return _to_response(item)


# DELETE - remove an item
@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item_service.delete_item(db, item_id)
    return {"message": f"Item {item_id} deleted"}
