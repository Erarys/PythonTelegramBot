from aiogram import Bot, Router, F
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import URLInputFile

from keyboards.admin_keyboard import (
    EditCatalogCallback,
    EditCategoryCallback,
    DeleteGoodsCallback,
    catalog_button,
    operating_mode_button,
    category_button_dict,
    delete_goods_button,
    brands
)
from DataBase.queries.orm import select_goods, insert_goods, delete_goods_orm, insert_posts, select_posts_msg
from text import category_translate_dict, goods_translate_dict, goods_text
from typing import Optional, Tuple
import os


class IsAdmin(BaseFilter):
    def __init__(self):
        self.ADMIN_ID = int(os.getenv("ADMIN_ID"))

    async def __call__(self, message: Message):
        if message.from_user.id == self.ADMIN_ID:
            return True
        await message.answer("Ваш запрос неверный")


class GoodsData(StatesGroup):
    # Класса для хранения товара для дальнейшего добавления
    choose_category = State()
    choose_brand = State()
    choose_name = State()
    choose_price = State()
    choose_characteristics = State()
    choose_photo = State()


router = Router()
router.message.filter(IsAdmin())


async def show_delete_goods(callback: CallbackQuery, goods_list: list) -> Optional[Tuple[int, list, list]]:
    """
    Асинхронная функция отправляет список товаров
    и возвращает их данные для удаления

    :param callback: для отправки запросов
    :param goods_list: список товаров
    :return: возвращает данные, необходимые для нахождения и удаления.
    """
    # ID поста
    post_id = callback.message.message_id
    # ID список всех отправленных товаров
    goods_ids = []
    # ID список всех отправленных сообщений
    message_ids = []

    if not goods_list:
        return

    for goods_tuple in goods_list:
        goods = goods_tuple[0]
        message = await callback.message.answer_photo(
            photo=goods.photo,
            caption=goods_text.format(
                name=goods.name,
                price=goods.price,
                characteristics=goods.characteristics
            ),
            reply_markup=delete_goods_button(post_id=post_id, goods_id=goods.id)

        )
        goods_ids.append(goods.id)
        message_ids.append(message.message_id)

    return post_id, message_ids, goods_ids


@router.message(Command("cancel"), GoodsData())
async def cancel_adding_goods(message: Message, state: FSMContext):
    await message.answer("Отменено ❎")
    await state.clear()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    await message.answer(
        text="Админский режим:\nВыберите категорию продукта:",
        reply_markup=catalog_button()
    )


@router.callback_query(EditCatalogCallback.filter())
async def show_category(callback: CallbackQuery, callback_data: EditCatalogCallback):
    await callback.message.answer(
        text=category_translate_dict[callback_data.catalog],
        reply_markup=category_button_dict[callback_data.catalog]
    )
    await callback.answer()


@router.callback_query(EditCategoryCallback.filter())
async def show_brands(callback: CallbackQuery, callback_data: EditCategoryCallback, state: FSMContext):
    await state.update_data(choose_category=callback_data.category)
    await callback.message.answer(
        text=f"{goods_translate_dict[callback_data.category]}\nВыберите производителя",
        reply_markup=brands[callback_data.category]
    )

    await state.set_state(GoodsData.choose_brand)
    await callback.answer()


@router.message(GoodsData.choose_brand)
async def choose_mode(message: Message, state: FSMContext):
    """
    Асинхронная функция отправляет кнопки для выбора
    режима работы.
    1) Удаления
    2) Добавление
    """
    await state.update_data(choose_brand=message.text)
    await message.answer("Выберите режим", reply_markup=operating_mode_button())


@router.callback_query(F.data == "delete_goods")
async def find_delete_goods(callback: CallbackQuery, state: FSMContext):
    """
    Асинхронная функция для удаления товара.
    :param callback:
    :param state: Хранится состояния выбранных категорий и брендов

    Когда мы выбираем режим удаления товара, то мы очищаем состояние
    после получения списка товаров
    """
    product = await state.get_data()
    # Обращаемся к бд, чтобы получить данные
    goods_list = await select_goods(
        category=product["choose_category"],
        brand=product["choose_brand"]
    )

    await callback.message.edit_text(text="Режим: удаления")
    # Проверяем на наличие товаров
    if goods_list:
        # Вызываем функцию для отправки товаров и получаем данные отправленных сообщений
        data_sends = await show_delete_goods(callback, goods_list)
        post_id, message_ids, goods_ids = data_sends
        # Сохраняем в бд данные про сообщение и товар
        await insert_posts(post_id, message_ids, goods_ids)
    else:
        await callback.message.answer("Товар не найден")

    await state.clear()
    await callback.answer()


@router.callback_query(DeleteGoodsCallback.filter())
async def remove_goods(callback: CallbackQuery, callback_data: DeleteGoodsCallback, bot: Bot):
    """
    Удаляем товар в базе данных, а также изменяем сообщение товара

    :param callback:
    :param callback_data: все необходимые данные о товаре для удаления
    :param bot:
    """
    # Удаления товара на базе данных
    await delete_goods_orm(callback_data.goods_id)
    # Через id и post находим id сообщения в бд
    message_id = await select_posts_msg(callback_data.post_id, callback_data.goods_id)

    # Если человек нажал на кнопку удаления, то мы его изменяем
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=message_id,
        media=InputMediaPhoto(media=URLInputFile(
            url="https://fastly.picsum.photos/id/329/400/300.jpg?hmac=CwK66llmWRlHvdMJ_jhsKnCDRFAyBMngiuHWYLQvEfQ",
            filename="remove_image.png"
        ),
            caption="Фотография был уничтожен"
        )
    )
    await callback.answer()


@router.callback_query(F.data == "add_goods")
async def add_goods(callback: CallbackQuery, state: FSMContext):
    """
    Асинхронная функция для добавления товара.

    :param callback:
    :param state: Хранит данные категорий и бренда

    Если выбрать режим добавления, то состояние не очищается
    """
    await callback.message.edit_text(text="Режим: добавления")
    await callback.message.answer(
        text="Добавление нового товара...\nВведите модель товара"
    )
    await state.set_state(GoodsData.choose_name)
    await callback.answer()


@router.message(GoodsData.choose_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(choose_name=message.text)
    await message.answer(text="Укажите цену: ")
    await state.set_state(GoodsData.choose_price)


@router.message(GoodsData.choose_price)
async def get_price(message: Message, state: FSMContext):
    await state.update_data(choose_price=message.text)
    await message.answer(text="Напишите описание товара: ")
    await state.set_state(GoodsData.choose_characteristics)


@router.message(GoodsData.choose_characteristics)
async def get_characteristics(message: Message, state: FSMContext):
    await state.update_data(choose_characteristics=message.text)
    await message.answer(text="Отправьте фото")
    await state.set_state(GoodsData.choose_photo)


@router.message(GoodsData.choose_photo)
async def get_photo(message: Message, state: FSMContext):
    """
    Асинхронная функция для сохранения товара в базе данных
    """
    await state.update_data(choose_photo=message.photo[-1].file_id)
    product = await state.get_data()

    # Добавляем в бд новый товар
    await insert_goods(
        product["choose_category"], product["choose_brand"],
        product["choose_name"], int(product["choose_price"]),
        product["choose_characteristics"], product["choose_photo"]
    )
    # Проверяем добавленный новый товар
    await show_result(message, product)
    await state.clear()


async def show_result(message: Message, product: dict):
    """
    Проверяем добавленный в базе данных товар
    :param message:
    :param product: Словарь хранящий данные о продукте
    :return:
    """
    name = product["choose_brand"] + " " + product["choose_name"]
    goods_tuple = await select_goods(brand=name, action=0)
    goods = goods_tuple[0]
    await message.answer_photo(
        goods.photo,
        caption=goods_text.format(
            name=goods.name,
            price=goods.price,
            characteristics=goods.characteristics
        )
    )
    await message.answer("Поздравляю все прошло успешно 🥳")