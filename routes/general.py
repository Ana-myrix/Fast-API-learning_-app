from fastapi import APIRouter

router = APIRouter(tags=["general"])


@router.get("/")
def hello():
    return {"message": "hello,world!"}


@router.get("/users/{user_id}")
def read_user(user_id: str):
    return {"user_id": user_id}
