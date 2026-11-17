from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True


class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    in_stock: bool | None = None



items_db: dict[int, Item] = {}

@app.get("/")
def hello():
    return {"message": "hello,world!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
@app.get("/users/{user_id}")
def read_user(user_id: str):
    return {"user_id" : user_id}


# POST - create a new item
@app.post("/items/{item_id}", status_code=201)
def create_item(item_id: int, item: Item):
    if item_id in items_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    items_db[item_id] = item
    return {"item_id": item_id, "item": item}


# PUT - replace an existing item completely
@app.put("/items/{item_id}")
def replace_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item
    return {"item_id": item_id, "item": item}


# PATCH - update only the fields that were sent
@app.patch("/items/{item_id}")
def update_item(item_id: int, changes: ItemUpdate):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = items_db[item_id].model_copy(
        update=changes.model_dump(exclude_unset=True)
    )
    items_db[item_id] = updated
    return {"item_id": item_id, "item": updated}


# DELETE - remove an item
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"message": f"Item {item_id} deleted"}
