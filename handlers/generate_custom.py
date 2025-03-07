from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, StateFilter, or_f
from config_data.config import Config, load_config
import qrcode
from PIL import Image
import logging

router = Router()
config: Config = load_config()

class LinkQr(StatesGroup):
    link_qr = State()


@router.message(F.text == '/QR')
async def all_message(message: Message, state: FSMContext) -> None:
    logging.info(f'all_message {message.chat.id} / {message.text}')
    await message.answer(text='Пришлите логотип и описание к нему для ссылки')
    await state.set_state(LinkQr.link_qr)


@router.message(F.photo, StateFilter(LinkQr.link_qr))
async def all_message(message: Message, state: FSMContext) -> None:
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
    logo_path = "logo.png"  # Укажите свой логотип
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