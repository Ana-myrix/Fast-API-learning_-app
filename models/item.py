from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Item(Base):
    __tablename__ = "items"

    # The client chooses the id, for example POST /items/1
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Float)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
