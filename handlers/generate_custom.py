from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
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
    text_qr = State()

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
    await message.answer_photo(photo=FSInputFile("example.png"))
    await state.set_state(LinkQr.link_qr)


@router.message(F.photo, StateFilter(LinkQr.link_qr))
async def all_message(message: Message, state: FSMContext, bot: Bot) -> None:
    # Извлекаем данные из подписи к фото
    data = message.caption or ""
    if not data.strip():
        await message.answer(text="Вы не указали ссылку под логотипом, попробуйте еще раз")
        return
    # Разбиваем данные на части и сохраняем в состоянии
    await state.update_data(
        url=data,  # Защита от IndexError
        user_id=message.from_user.id
    )

    # Скачиваем и сохраняем логотип
    await download_photo(message=message, bot=bot)
    logo_path = f"QR/{message.from_user.id}.png"
    await state.update_data(logo_path=logo_path)  # Сохраняем путь к лого в состоянии
    await message.answer(text="Если хотите ,чтобы под qr был текст отправьте его или нажмите на кнопку",
                         reply_markup=await no_button(answer="No")) #тут измените путь к функции если измените ее расположение
    await state.set_state(LinkQr.text_qr)

@router.callback_query(F.data == 'No', StateFilter(LinkQr.link_qr))
async def handle_no_text(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'handle_no_text: {callback.message.chat.id}')
    # Получаем все сохраненные данные из состояния
    state_data = await state.get_data()

    # Создаем QR без текста
    photo = await start_create_qr(
        url=state_data['url'],  # Берем url из состояния
        text="",  # Явно указываем пустой текст
        tg_id=state_data['user_id'],  # ID из состояния
        logo_path=state_data['logo_path']  # Путь к лого из состояния
    )

    await callback.message.answer_photo(photo=photo)
    await state.clear()

@router.message(StateFilter(LinkQr.text_qr))
async def all_message(message: Message, state: FSMContext, bot: Bot) -> None:
    data = message.caption
    # Получаем все сохраненные данные из состояния
    state_data = await state.get_data()

    # Создаем QR без текста
    photo = await start_create_qr(
        url=state_data['url'],  # Берем url из состояния
        text=data,
        tg_id=state_data['user_id'],  # ID из состояния
        logo_path=state_data['logo_path']  # Путь к лого из состояния
    )
    await message.answer_photo(photo=photo)
    await state.clear()



#эту часть кода можно перенести в файл с подобным функционалом
#тут продумана возможность расширения функционала
async def no_button(answer: str) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text=answer, callback_data=answer)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]]
    )
    return keyboard