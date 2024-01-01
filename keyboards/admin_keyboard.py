from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton, ReplyKeyboardMarkup
)
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    ReplyKeyboardBuilder
)
from typing import List


class EditCatalogCallback(CallbackData, prefix="edit_catalog"):
    catalog: str


class EditCategoryCallback(CallbackData, prefix="edit_category"):
    category: str


class DeleteGoodsCallback(CallbackData, prefix="delete"):
    post_id: int
    goods_id: int


def factory_button_category(categories: List[str], category_callback: List[str]) -> InlineKeyboardMarkup:
    """
    Функция для создания инлайн кнопки
    для выбора категорий товаров.

    :param categories: Список называний категорий
    :param category_callback: callback для кнопки

    Эти списки по длине равны и через цикл передаются
    параллельно в InlineKeyboardButton()
    """
    builder = InlineKeyboardBuilder()

    for text, callback in zip(categories, category_callback):
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=EditCategoryCallback(category=callback).pack()
        )
        )

    builder.adjust(2)
    return builder.as_markup()


def factory_button_brands(brand_names: List[str]) -> ReplyKeyboardMarkup:
    """
    Функция для создания обычной кнопки
    для выбора бренда

    :param brand_names: Список названий брендов
    """
    builder = ReplyKeyboardBuilder()

    for name in brand_names:
        builder.add(KeyboardButton(text=name))

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def operating_mode_button() -> InlineKeyboardMarkup:
    """
    Функция для создания инлайн кнопки
    для выбора админского режима:
    1)Добавление нового товара
    2)Удаление старых товаров
    """
    button = [
        [InlineKeyboardButton(text="Добавить новый продукт", callback_data="add_goods")],
        [InlineKeyboardButton(text="Удалить старый продукт", callback_data="delete_goods")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=button)


def delete_goods_button(post_id: int, goods_id: int) -> InlineKeyboardMarkup:
    """
    Функция для создания инлайн кнопки
    который хранит информацию товара и поста

    :param post_id: ID - самого основного поста
    :param goods_id: ID - определенного товара в БД
    """
    button = [
        [
            InlineKeyboardButton(
                text="Удалить",
                callback_data=DeleteGoodsCallback(post_id=post_id, goods_id=goods_id).pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=button)


def catalog_button():
    """
    Функция для создания кнопки для каталогов
    """
    buttons = [
        [
            InlineKeyboardButton(
                text='📱 Телефоны и ⌚ гаджеты',
                callback_data=EditCatalogCallback(catalog='phone_gadgets').pack()
            ),
            InlineKeyboardButton(
                text='🏠 Бытовая техника',
                callback_data=EditCatalogCallback(catalog="appliances").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text='🔊 Аудио, 📹 Видео',
                callback_data=EditCatalogCallback(catalog="periphery").pack()
            ),
            InlineKeyboardButton(
                text='💻 Компьютеры',
                callback_data=EditCatalogCallback(catalog="computer").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text='📺 Телевизоры',
                callback_data=EditCategoryCallback(category="tv").pack()
            ),
            InlineKeyboardButton(
                text='🧰 Строительсто и ремонт',
                callback_data=EditCatalogCallback(catalog="tools").pack()
            )
        ],
        [
            InlineKeyboardButton(text='⬇️ Еще', callback_data='more')
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Создаем словарь, который будет содержать категории товаров и соответствующие кнопки
category_button_dict = {
    "phone_gadgets": factory_button_category(
        categories=["📱 Смартфоны", "⌚ Смарт часы", "🔌 Адаптеры", "📲 Чехлы"],
        category_callback=["phone", "watch", "charger", "case"]
    ),
    "appliances": factory_button_category(
        categories=["🫖 Электрочайник", "🎁 Микроволновка", "🧹 Пылесос", "🎛 Стиральная машина"],
        category_callback=["kettle", "microwave", "vacuum", "washing"]
    ),
    "periphery": factory_button_category(
        categories=["📢 Портативные колонки", "📹 Видеокамеры"],
        category_callback=["column", "camera"]
    ),
    "computer": factory_button_category(
        categories=["💻 Ноутбуки", "🖥 Настольные компьютеры"],
        category_callback=["laptop", "computer"]
    ),
    "tv": factory_button_brands(
        brand_names=["LG", "Samsung", "Xiaomi", "Yasin"]
    ),
    "tools": factory_button_category(
        categories=["🔧 Наборы инструментов", "⚒ Шуруповерты", "⚒ Дрели"],
        category_callback=["set_tools", "screwdrivers", "drills"]
    )
}

# Создаем словарь, который будет содержать категории товаров и соответствующие бренды кнопки
brands = {
    "phone": factory_button_brands(brand_names=["Apple", "Samsung", "Xiaomi", "Huawei"]),
    "watch": factory_button_brands(brand_names=["Apple", "Samsung", "Xiaomi", "Huawei"]),
    "charger": factory_button_brands(brand_names=["Apple", "Samsung", "Xiaomi", "Huawei"]),
    "case": factory_button_brands(brand_names=["Apple", "Samsung", "Xiaomi", "Huawei"]),
    "kettle": factory_button_brands(brand_names=["Tefal", "Bosch", "Philips", "Braun"]),
    "microwave": factory_button_brands(brand_names=["ARG", "Hansa", "LG", "Magna"]),
    "vacuum": factory_button_brands(brand_names=["LG", "Samsung", "Xiaomi", "Philips"]),
    "washing": factory_button_brands(brand_names=["LG", "Samsung", "Beko", "Haier"]),
    "column": factory_button_brands(brand_names=["JBL", "Sony", "Vipe", "Xiaomi"]),
    "camera": factory_button_brands(brand_names=["Sony", "Canon", "Panasonic", "Fujifilm"]),
    "computer": factory_button_brands(brand_names=["Ucomp", "ITBRO", "Cassian", "Wintek"]),
    "laptop": factory_button_brands(brand_names=["Acer", "Apple", "ASUS", "HP"]),
    "tv": factory_button_brands(brand_names=["LG", "Samsung", "Xiaomi", "Yasin"]),
    "set_tools": factory_button_brands(brand_names=["Force", "ROCKFORCE"]),
    "screwdrivers": factory_button_brands(brand_names=["Bosch", "CROWN", "ALTECO"]),
    "drills": factory_button_brands(brand_names=["Bosch", "CROWN", "ALTECO"])
}
