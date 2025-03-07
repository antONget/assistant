from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, StateFilter, or_f
from config_data.config import Config, load_config
import qrcode
from PIL import Image
import os
import logging

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
        photo_path = os.path.join(DOWNLOADS_FOLDER, f'{message.from_user.id}.jpg')
        await photo_file.download(photo_path)
        # Далее можно провести необходимую обработку или отправить ответ пользователю
        await message.reply(f'Фотография сохранена: {photo_path}')



@router.message(F.text == '/QR')
async def all_message(message: Message, state: FSMContext) -> None:
    logging.info(f'all_message {message.chat.id} / {message.text}')
    await message.answer(text='Пришлите логотип и описание к нему для ссылки')
    await state.set_state(LinkQr.link_qr)


@router.message(F.photo, StateFilter(LinkQr.link_qr))
async def all_message(message: Message, state: FSMContext, bot: Bot) -> None:
    # 🔹 Данные для QR-кода (ссылка или текст)
    data = message.text

    # 🔹 Генерация QR-кода
    qr = qrcode.QRCode(
        version=5,  # Размер QR-кода (1-40, чем больше, тем плотнее)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Устойчивость к повреждениям
        box_size=10,  # Размер каждого квадрата
        border=4,  # Размер границы
    )
    qr.add_data(data)
    qr.make(fit=True)

    # 🔹 Создание изображения QR-кода
    qr_img = qr.make_image(fill="black", back_color="white").convert("RGB")

    # 🔹 Добавление логотипа (если есть)
    await download_photo(message=message, bot=bot)
    logo_path = f"{message.from_user.id}.png"  # Укажите свой логотип
    try:
        logo = Image.open(logo_path)

        # Приводим логотип к нужному размеру
        logo_size = (qr_img.size[0] // 4, qr_img.size[1] // 4)
        logo = logo.resize(logo_size)

        # Вставляем логотип в центр QR-кода
        pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
        qr_img.paste(logo, pos)

    except FileNotFoundError:
        await message.answer("⚠ Логотип не найден, создаем QR-код без него.")

    # 🔹 Сохранение QR-кода
    output_file = "qr_code.png"
    qr_img.save(output_file)
    await message.answer_photo(photo=qr_img)