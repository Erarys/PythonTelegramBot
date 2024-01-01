from aiogram import Bot, Dispatcher
from handlers import handlers, admin
from handlers import goods_handler, assistant_handler
from DataBase.queries.orm import create_table

import os
import asyncio
import logging


async def main():
    """
    Самый основной функция
    Соединяет все роутеры к диспетчеру
    :return:
    """
    bot = Bot(token=os.getenv("TOKEN"))
    dp = Dispatcher()
    dp.include_router(admin.router)
    dp.include_router(assistant_handler.router)
    dp.include_router(handlers.router)
    dp.include_router(goods_handler.router)
    await create_table()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

