from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from DataBase.database import Base


class GoodsTableORM(Base):
    __tablename__ = "goods"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[str] = mapped_column(String(length=20))
    name: Mapped[str] = mapped_column(String(length=100))
    price: Mapped[int]
    characteristics: Mapped[str] = mapped_column(String(length=300))
    photo: Mapped[str] = mapped_column(String(length=100))


class PostsTableORM(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int]
    message_id: Mapped[int] = mapped_column(primary_key=True)
    goods_id: Mapped[int] = mapped_column(primary_key=True)
