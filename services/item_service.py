from sqlalchemy.orm import Session

from models.item import Item
from services.errors import AppError


def create_item(db: Session, item_id: int, fields: dict) -> Item:
    if db.get(Item, item_id) is not None:
        raise AppError(400, "Item already exists")
    item = Item(id=item_id, **fields)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def replace_item(db: Session, item_id: int, fields: dict) -> Item:
    item = db.get(Item, item_id)
    if item is None:
        raise AppError(404, "Item not found")
    for field, value in fields.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item_id: int, changes: dict) -> Item:
    """Change only the fields that were sent."""
    return replace_item(db, item_id, changes)


def delete_item(db: Session, item_id: int) -> None:
    item = db.get(Item, item_id)
    if item is None:
        raise AppError(404, "Item not found")
    db.delete(item)
    db.commit()
