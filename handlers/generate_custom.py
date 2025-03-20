from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from config_data.config import Config, load_config
import os
import logging

from qr_creator import start_create_qr

router = Router()
config: Config = load_config()

class LinkQr(StatesGroup):
    link_qr = State()


DOWNLOADS_FOLDER = 'QR'

async def download_photo(message: Message, bot: Bot):
    # Проверяем, есть ли файл в сообщении
    if message.photo:
        # Получаем информацию о фотографии
        photo_info = message.photo[-1]
        # Получаем объект File для скачивания
        photo_file = await bot.get_file(photo_info.file_id)
        # Ссылка для скачивания файла
        photo_url = f'https://api.telegram.org/file/bot{config.tg_bot.token}/{photo_file.file_path}'
        # Создаём папку для сохранения файлов, если её нет
        if not os.path.exists(DOWNLOADS_FOLDER):
            os.makedirs(DOWNLOADS_FOLDER)
        # Загружаем фотографию в локальную папку
        photo_path = os.path.join(DOWNLOADS_FOLDER, f'{message.from_user.id}.png')
        await bot.download_file(photo_file.file_path, photo_path)
        # Далее можно провести необходимую обработку или отправить ответ пользователю
        await message.reply(f'Фотография сохранена: {photo_path}')


@router.message(F.text == '/QR')
async def all_message(message: Message, state: FSMContext) -> None:
    logging.info(f'all_message {message.chat.id} / {message.text}')
    await message.answer(text='Пришлите логотип , ссылку и текст который будет под qr через _')
    await message.answer("Пример: https://example.com_Scan Me!")
    await message.answer_photo(photo="example.png")
    await state.set_state(LinkQr.link_qr)


@router.message(F.photo, StateFilter(LinkQr.link_qr))
async def all_message(message: Message, state: FSMContext, bot: Bot) -> None:
    # 🔹 Данные для QR-кода (ссылка или текст)
    data = message.caption
    if not "_" in data:
        data = f"{data}_{data}"
    data = data.split("_")
    await download_photo(message=message, bot=bot)
    logo_path = f"QR/{message.from_user.id}.png"  # Укажите свой логотип
    photo = await start_create_qr(url=data[0], text=data[1], tg_id=message.from_user.id, logo_path=logo_path)
    await message.answer_photo(photo=photo)
