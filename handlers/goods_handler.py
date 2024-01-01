from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

from DataBase.queries.orm import select_goods
from keyboards.goods_keyboard import (
    CategoryCallback,
    BrandsCallback,
    USBCallback,
    category_dict,
    brands_dict,
    usb_type_button,
    select_goods_button,
    price_button
)
from text import goods_translate_dict, category_translate_dict, goods_text
from keyboards.keyboard import CatalogCallback


class USBType(StatesGroup):
    """Хранит тип usb порта"""
    types = State()


class GoodsData(StatesGroup):
    """Хранит данные товара"""
    price = State()
    category = State()


class GoodsSendData(StatesGroup):
    """Хранит данные отправляемых данных"""
    generator_goods = State()
    len = State()


def generatorGoods(goods_ls: list):
    """
    Функция генератор для получения товара разделяя их
    :param goods_ls: Список товаров
    :return: Кортеж из списка товара и количества выведенных товаров
    """
    goods_return = []

    for index, goods in enumerate(goods_ls):
        goods_return.append(goods[0])

        if index % 2 == 1:
            yield goods_return, len(goods_ls)-index-1
            goods_return.clear()

    yield goods_return, 0


router = Router()


@router.callback_query(F.data == "next")
async def show_goods(callback: CallbackQuery, state: FSMContext):
    """
    Асинхронная функция для отправки товаров.

    :param callback:
    :param state: Содержит генератор

    С помощью генератора мы отправляем пользователю
    товар постепенно и когда пользователь нажимает
    на кнопку с колбэком next мы снова вызываем эту
    функцию.
    """
    goods_data = await state.get_data()

    if callback.data == "next":
        await callback.message.edit_text("Далее")

    for goods_list, remainder in goods_data["generator_goods"]:
        for goods in goods_list:
            await callback.message.answer_photo(
                photo=goods.photo,
                caption=goods_text.format(
                    name=goods.name,
                    price=goods.price,
                    characteristics=goods.characteristics
                )
            )

        if remainder != 0:
            await callback.message.answer(
                text="Осталось {}".format(remainder),
                reply_markup=select_goods_button()
            )
            break
    else:
        await callback.message.answer("Найдено {} результатов".format(goods_data["len"]), reply_markup=None)


async def get_goods(callback: CallbackQuery, state: FSMContext, brand="_", category="_", price="all", characteristics="_"):
    """
    Асинхронная функция для получения товаров.

    Args:
        callback: Объект CallbackQuery.
        state: Объект FSMContext для управления состоянием.
        brand: Параметр для фильтрации по бренду (по умолчанию "_").
        category: Параметр для фильтрации по категории (по умолчанию "_").
        price: Параметр для фильтрации по ценовой категории (по умолчанию "all").
        characteristics: Параметр для фильтрации по характеристикам (по умолчанию "_").

    Описание:
        1. Вызывает функцию select_goods для получения товаров с заданными параметрами.
        2. Обновляем данные в состоянии: сохраняем "generator_goods" и количество товаров.
        3. Вызывает функцию show_goods для отображения товаров.
    """
    goods = await select_goods(brand=brand, category=category, price=price, characteristic=characteristics)

    await state.update_data(generator_goods=generatorGoods(goods))
    await state.update_data(len=len(goods))

    # Мы вызываем эту функцию для запуская генератора
    await show_goods(callback, state)


@router.callback_query(CatalogCallback.filter())
async def show_category(callback: CallbackQuery, callback_data: CatalogCallback):
    await callback.message.answer(
        text=category_translate_dict[callback_data.catalog],
        reply_markup=category_dict[callback_data.catalog]
    )
    await callback.answer()


@router.callback_query(CategoryCallback.filter())
async def show_price(callback: CallbackQuery, callback_data: CategoryCallback, state: FSMContext):
    """
    Асинхронная функция для сохранения категорий и предложения выбора ценовой категории.
    """
    await state.update_data(category=callback_data.category)
    await state.set_state(GoodsData.price)
    await callback.message.answer(text="Выберите ценовую категорию:", reply_markup=price_button())
    await callback.answer()


@router.callback_query(GoodsData.price)
async def get_price(callback: CallbackQuery, state: FSMContext):
    """
    Асинхронная функция для получения ценовой категорий и сохранения в состояния

    :param callback:
    :param state:

    Если пользователь выбирает категорию "charger",
    то ему необходимо будет определиться с типом зарядки.
    В противном случае предлагается выбрать бренд товара.
    """
    await state.update_data(price=callback.data)
    data = await state.get_data()

    if data["category"] == "charger":
        await state.set_state(USBType.types)
        await callback.message.answer(
            text="Выберите тип зарядки:",
            reply_markup=usb_type_button()
        )
    else:
        await callback.message.answer(
            text=goods_translate_dict[data["category"]],
            reply_markup=brands_dict[data["category"]]
        )
    await state.set_state(None)
    await callback.answer()


@router.callback_query(USBCallback.filter())
async def show_usb_brands(callback: CallbackQuery, callback_data: USBCallback, state: FSMContext):
    """
    Асинхронная функция для получения типа зарядки
    и предлагается выбрать бренд.
    """
    await state.update_data(types=callback_data.types)
    await callback.message.answer(text="Зарядки", reply_markup=brands_dict["charger"])
    await callback.answer()


@router.callback_query(BrandsCallback.filter())
async def sort_show_goods(callback: CallbackQuery, callback_data: BrandsCallback, state: FSMContext):
    """
    Асинхронная функция для получения всех данных
    :param callback:
    :param callback_data: хранятся бренд и категория
    :param state: хранятся ценовая категория

    Если пользователь выбирает категорию "charger",
    то ему указываем дополнительные параметры "characteristics".
    В противном случае без него.
    """
    data = await state.get_data()
    if callback_data.category == "charger":
        await get_goods(
            callback,
            state,
            brand=callback_data.brand,
            category=callback_data.category,
            characteristics=data["types"]
        )
    else:
        await get_goods(
            callback,
            state,
            brand=callback_data.brand,
            price=data["price"],
            category=callback_data.category
        )

    await callback.answer()


@router.callback_query(F.data.startswith("show"))
async def show_category_goods(callback: CallbackQuery, state: FSMContext):
    """
    Асинхронная функция для получения товаров одной категории, но разного бренда.

    Описание:
        1. Получаем данные из состояния.
        2. Выбираем товары для указанной категории и ценовой категории.
        3. Обновляем данные в состоянии: сохраняем "generator_goods" и "len" его длину.
        4. Вызываем функцию для отображения товаров.
        5. Запускаем генератор
    """
    data = await state.get_data()
    goods_list = await select_goods(category=callback.data.split("_")[1], price=data["price"])

    await state.update_data(generator_goods=generatorGoods(goods_list))
    await state.update_data(len=len(goods_list))

    # Начинаем отправлять товар
    await show_goods(callback, state)
    await callback.answer()


