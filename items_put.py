from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True


# Simple in-memory storage (data is lost when the server restarts)
items_db: dict[int, Item] = {}


# PUT - create the item if it does not exist, otherwise replace it completely
@app.put("/items/{item_id}")
def put_item(item_id: int, item: Item, response: Response):
    created = item_id not in items_db
    items_db[item_id] = item
    response.status_code = 201 if created else 200
    return {"item_id": item_id, "item": item, "created": created}
