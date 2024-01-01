from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List


class CategoryCallback(CallbackData, prefix="category"):
    """
    Callback кнопки выбора категорий,
    который хранит в себе информацию
    товара.
    """
    category: str


class BrandsCallback(CallbackData, prefix="brand"):
    """
    Callback кнопки выбора брендов,
    который хранит в себе информацию
    товара.
    """
    brand: str
    category: str


class USBCallback(CallbackData, prefix="usb"):
    """
    Callback кнопки выбора типа коннектора
    который хранит в себе информацию
    """
    types: str


def factory_category_button(category: List[str], category_callback: List[str]) -> InlineKeyboardMarkup:
    """
    Функция для создания инлайн кнопки категорий товаров

    :param category: список всех категорий
    :param category_callback: список всех именований для кнопки
    """
    keyboards = InlineKeyboardBuilder()

    for goods, goods_callback in zip(category, category_callback):
        keyboards.add(InlineKeyboardButton(
            text=goods,
            callback_data=CategoryCallback(category=goods_callback).pack())
        )

    keyboards.adjust(2)
    return keyboards.as_markup()


def factory_brands_button(brands: List[str], category: str):
    """
    Функция для создания инлайн кнопки под выбор
    брендов в категорий

    :param brands: Список всех брендов
    :param category:
    """
    keyboards = InlineKeyboardBuilder()

    for brand in brands:
        keyboards.add(
            InlineKeyboardButton(text=brand, callback_data=BrandsCallback(brand=brand.lower(), category=category).pack())
        )
    keyboards.add(InlineKeyboardButton(text="Показать", callback_data=f"show_{category.lower()}"))
    keyboards.adjust(2)
    return keyboards.as_markup()


def usb_type_button():
    button = [
        [
            InlineKeyboardButton(
                text="USB Type-C",
                callback_data=USBCallback(types="type-c").pack()
            ),
            InlineKeyboardButton(
                text="Micro USB",
                callback_data=USBCallback(types="micro").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Lightning",
                callback_data=USBCallback(types="lightning").pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=button)


def select_goods_button():
    kb = [
        [
            InlineKeyboardButton(text="Показать еще ⬇️", callback_data="next")
        ]
    ]
    keyboards = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboards


def price_button() -> InlineKeyboardMarkup:
    """
    Функция для создания инлайн кнопки под
    выбор ценовой категорий
    """
    kb = [
        [
            InlineKeyboardButton(text="Бюджетный", callback_data="budget"),
            InlineKeyboardButton(text="Дорогой", callback_data="expensive")
        ],
        [
            InlineKeyboardButton(text="Все", callback_data="all")
        ]
    ]
    keyboards = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboards


# Создаем словарь, который будет содержать категории товаров и соответствующие кнопки
category_dict = {
    "phone_gadgets": factory_category_button(
        category=["📱 Смартфоны", "⌚ Смарт часы", "🔌 Адаптеры", "📲 Чехлы"],
        category_callback=["phone", "watch", "charger", "case"]
        ),
    "appliances": factory_category_button(
        category=["🫖 Электрочайник", "🎁 Микроволновка",  "🧹 Пылесос", "🎛 Стиральная машина"],
        category_callback=["kettle", "microwave", "vacuum", "washing"]
        ),
    "periphery": factory_category_button(
        category=["📢 Портативные колонки", "📹 Видеокамеры"],
        category_callback=["column", "camera"]
        ),
    "computer": factory_category_button(
        category=["💻 Ноутбуки", "🖥 Настольные компьютеры"],
        category_callback=["laptop", "computer"]
    ),
    "tv": factory_brands_button(
        brands=["LG", "Samsung", "Xiaomi", "Yasin"],
        category="tv"
    ),
    "tools": factory_category_button(
        category=["🔧 Наборы инструментов", "⚒ Шуруповерты", "⚒ Дрели"],
        category_callback=["set_tools", "screwdrivers", "drills"]
    )
}

# Создаем словарь, который будет содержать категории товаров и соответствующие бренды инлайн кнопки
brands_dict = {
    "phone": factory_brands_button(brands=["Apple", "Samsung", "Xiaomi", "Huawei"], category="phone"),
    "watch": factory_brands_button(brands=["Apple", "Samsung", "Xiaomi", "Huawei"], category="watch"),
    "charger": factory_brands_button(brands=["Apple", "Samsung", "Xiaomi", "Huawei"], category="charger"),
    "case": factory_brands_button(brands=["Apple", "Samsung", "Xiaomi", "Huawei"], category="case"),
    "kettle": factory_brands_button(brands=["Tefal", "Bosch", "Philips", "Braun"], category="kettle"),
    "microwave": factory_brands_button(brands=["ARG", "Hansa", "LG", "Magna"], category="microwave"),
    "vacuum": factory_brands_button(brands=["LG", "Samsung", "Xiaomi", "Philips"], category="vacuum"),
    "washing": factory_brands_button(brands=["LG", "Samsung", "Beko", "Haier"], category="washing"),
    "column": factory_brands_button(brands=["JBL", "Sony", "Vipe", "Xiaomi"], category="column"),
    "camera": factory_brands_button(brands=["Sony", "Canon", "Panasonic", "Fujifilm"], category="camera"),
    "computer": factory_brands_button(brands=["Ucomp", "ITBRO", "Cassian", "Wintek"], category="computer"),
    "laptop": factory_brands_button(brands=["Acer", "Apple", "ASUS", "HP"], category="laptop"),
    "set_tools": factory_brands_button(brands=["Force", "ROCKFORCE"], category="set_tools"),
    "screwdrivers": factory_brands_button(brands=["Bosch", "CROWN", "ALTECO"], category="screwdrivers"),
    "drills": factory_brands_button(brands=["Bosch", "CROWN", "ALTECO"], category="drills")
    }
