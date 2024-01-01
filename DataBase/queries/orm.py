from sqlalchemy import select, and_, delete, func
from DataBase.database import engine, Base, factory_session
from DataBase.models import GoodsTableORM, PostsTableORM
from typing import List


async def create_table():
    # Создаем все таблицы наследованные из класса Base
    Base.metadata.create_all(engine)


async def insert_goods(category_id: str, brand: str, name: str, price: int, characteristics: str, photo: str):
    # Добавляем товар в таблицу
    with factory_session() as session:
        with session.begin():
            stmt = GoodsTableORM(
                category_id=category_id,
                name=f"{brand} {name}",
                price=price,
                characteristics=characteristics,
                photo=photo
            )
            session.add(stmt)


async def select_avg_price(brand="_", category="_"):
    # Вычисляем среднее арифметическое цен товара.
    with factory_session() as session:
        stmt = select(func.avg(GoodsTableORM.price)).where(
            GoodsTableORM.name.like(f"{brand}%"),
            GoodsTableORM.category_id.like(f"{category}%"))

        price = session.execute(stmt)
        return price.scalar() or 0


async def select_goods(brand="_", category="_", characteristic="_", price="all", action=1) -> List[tuple] | tuple:
    """
    Запрос из базы данных, нужных товаров по фильтрам

    :param brand:
    :param category:
    :param characteristic:
    :param price: Если all, то все.
                  Если expensive, то больше средней цены.
                  Если budget, то ниже средней цены
    :param action: Если 1, то все данные. А если 0, то только первый.
    """
    avg_price = await select_avg_price(brand=brand, category=category)

    if price == "expensive":
        stmt = select(GoodsTableORM).where(
            and_(
                GoodsTableORM.name.like(f"{brand}%"),
                GoodsTableORM.category_id.like(f"{category}%"),
                GoodsTableORM.characteristics.like(f"%{characteristic}%"),
                GoodsTableORM.price >= avg_price
            )

        )
    elif price == "budget":
        stmt = select(GoodsTableORM).where(
            and_(
                GoodsTableORM.name.like(f"{brand}%"),
                GoodsTableORM.category_id.like(f"{category}%"),
                GoodsTableORM.characteristics.like(f"%{characteristic}%"),
                GoodsTableORM.price <= avg_price
            )
        )
    else:
        stmt = select(GoodsTableORM).where(
            and_(
                GoodsTableORM.name.like(f"{brand}%"),
                GoodsTableORM.category_id.like(f"{category}%"),
                GoodsTableORM.characteristics.like(f"%{characteristic}%")
            )
        )

    with factory_session() as session:
        goods = session.execute(stmt)
        session.commit()

        if action:
            return goods.all()
        else:
            return goods.first()


async def delete_goods_orm(id: int):
    # Удаляем товар из таблицы с помощью ID товара
    with factory_session() as session:
        with session.begin():
            stmt = delete(GoodsTableORM).where(GoodsTableORM.id == id)

            session.execute(stmt)


async def insert_posts(posts_id: int, message_ids: list, goods_ids: list):
    # Добавляем группу сообщений для дальнейшего использования
    with factory_session() as session:
        for message_id, goods_id in zip(message_ids, goods_ids):
            stmt = PostsTableORM(
                post_id=posts_id,
                message_id=message_id,
                goods_id=goods_id
            )
            session.add(stmt)

        session.commit()


async def select_posts_msg(post_id: int, goods_id: int):
    """
    Получаем id сообщения, по id товара

    :param post_id: id хэндлера
    :param goods_id: id товаров

    Когда мы отправляем список товаров, для удаления
    то мы сохраняем в базе данных.
    """
    with factory_session() as session:
        stmt = select(PostsTableORM.message_id).where(
            PostsTableORM.post_id == post_id,
            PostsTableORM.goods_id == goods_id
        )
        post = session.execute(stmt)
        message_id = post.scalar()
        return message_id












