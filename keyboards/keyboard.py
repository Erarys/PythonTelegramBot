from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData


class CatalogCallback(CallbackData, prefix="catalog"):
    catalog: str


def catalog_button() -> InlineKeyboardMarkup:
    """
        Функция для создания кнопки для каталогов
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="📱 Телефоны и ⌚ гаджеты",
                callback_data=CatalogCallback(catalog="phone_gadgets").pack()
                ),
            InlineKeyboardButton(
                text="🏠 Бытовая техника",
                callback_data=CatalogCallback(catalog="appliances").pack()
                )
         ],
        [
            InlineKeyboardButton(
                text="🔊 Аудио, 📹 Видео",
                callback_data=CatalogCallback(catalog="periphery").pack()
                ),
            InlineKeyboardButton(
                text="💻 Компьютеры",
                callback_data=CatalogCallback(catalog='computer').pack()
                )
        ],
        [
            InlineKeyboardButton(
                text="📺 Телевизоры",
                callback_data=CatalogCallback(catalog='tv').pack()
                ),
            InlineKeyboardButton(
                text="🧰 Строительство и ремонт",
                callback_data=CatalogCallback(catalog="tools").pack()
                )
        ],
        [
            InlineKeyboardButton(
                text="🤖 Вызывать помощь",
                callback_data='ai_helper'
                )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard
