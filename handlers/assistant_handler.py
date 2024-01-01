from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    ServiceContext
)
from llama_index.indices.struct_store import NLSQLTableQueryEngine
from llama_index.llms import OpenAI
from DataBase.database import engine
from llama_index import SQLDatabase

from text import ai_settings
import os


class QuestionType(CallbackData, prefix="question"):
    """
    Callback кнопки выбора режима ИИ,
    хранит в себе информацию
    """
    type: str


class AIHelper(StatesGroup):
    question_type = State()


router = Router()


def get_ai_button() -> InlineKeyboardMarkup:
    """
    Функция для создания инлайн кнопки для ИИ
    режима.
    """
    button = [
        [
            InlineKeyboardButton(text="Вопрос о товаре", callback_data=QuestionType(type="question").pack()),
            InlineKeyboardButton(text="Запрос о товаре", callback_data=QuestionType(type="request").pack())
        ],
        [
            InlineKeyboardButton(text="Конец диалога", callback_data="stop_ai")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=button)


async def answer_question(question: str) -> str:
    """
    Асинхронная функция для обработки вопроса
    пользователя

    :param question:

    Если в корневой папке не находится папка
    storage, то мы ищем папку storage чтобы
    прочитать находящийся внутри данные.
    И создаем storage.

    А если файл с названием storage все таки
    находится в корневой папке, то получаем
    данные из него.
    """
    llm = OpenAI(temperature=0, model="gpt-3.5-turbo", max_tokens=140)
    service_context = ServiceContext.from_defaults(llm=llm)

    if not os.path.exists("../storage"):
        document = SimpleDirectoryReader("data").load_data()
        index = VectorStoreIndex(document, service_context=service_context)
        index.storage_context.persist()
    else:
        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(storage_context, service_context=service_context)

    query_engine = index.as_query_engine()
    response = query_engine.query(question)

    return response.response


async def answer_request(question: str) -> str:
    """
    Асинхронная функция для обработки слов в
    sql запросы, чтобы получить данные о товарах.

    :param question:
    """
    # Подключаем движок алхимий и название таблицы
    sql_database = SQLDatabase(engine, include_tables=["goods"])

    query_engine = NLSQLTableQueryEngine(sql_database)
    response = query_engine.query(question)

    return response.response


@router.message(Command("stop"), AIHelper.question_type)
async def stop_state(message: Message, state: FSMContext):
    """
    Функция отменяет состояние чтобы пользователь мог
    выйти из режима вопросов
    """
    await message.answer(text="Ваши действие отменено ❎")
    await state.clear()


@router.callback_query(F.data == "stop_ai")
async def stop_ai(callback: CallbackQuery, state: FSMContext):
    """
    Если пользователь нажимает на кнопку
    остановки ИИ, то срабатывает этот
    хэндлер.
    """
    await callback.message.edit_text(text=callback.message.text)
    await callback.message.answer(text="Я рад вам помочь")
    await callback.answer()
    await state.clear()


@router.callback_query(F.data == "ai_helper")
async def assistant(callback: CallbackQuery):
    """
    Позволяет выбрать режим работы ИИ
    """
    await callback.message.answer(
        text="Выберите режим общения:",
        reply_markup=get_ai_button()
    )
    await callback.answer()


@router.callback_query(QuestionType.filter())
async def ask(callback: CallbackQuery, callback_data: QuestionType, state: FSMContext):
    """
    Настрайвает состояние на режим работы ИИ.
    """

    await state.set_state(AIHelper.question_type)
    await state.update_data(question_type=callback_data.type)
    await callback.message.edit_text(callback.message.text)
    await callback.message.answer("Здравствуйте чем я вам могу помочь?")


@router.message(AIHelper.question_type)
async def answer_user(message: Message, state: FSMContext):
    """
    Отвечает на вопрос пользователя.

    :param message:
    :param state: хранит информацию о режиме работы
    """

    # Настрайвается на корректный ответ
    question = ai_settings.format(message.text)
    data = await state.get_data()

    if data["question_type"] == "question":
        answer = await answer_question(question)
    else:
        answer = await answer_request(question)

    await message.answer(text=answer, reply_markup=get_ai_button())



