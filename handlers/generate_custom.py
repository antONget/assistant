from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from config_data.config import Config, load_config, load_constant
import os
import logging

from qr_creator import start_create_qr, file_in_folder

router = Router()
config: Config = load_config()
const = load_constant()

class LinkQr(StatesGroup):
    link_qr = State()
    text_qr = State()


async def download_photo(message: Message, bot: Bot):
    # Проверяем, есть ли файл в сообщении
    if message.photo:
        # Получаем информацию о фотографии
        photo_info = message.photo[-1]
        # Получаем объект File для скачивания
        photo_file = await bot.get_file(photo_info.file_id)
        # Создаём папку для сохранения файлов, если её нет
        if not os.path.exists(const.download):
            os.makedirs(const.download)
        # Загружаем фотографию в локальную папку
        photo_path = os.path.join(const.download, f'{message.from_user.id}.png')
        await bot.download_file(photo_file.file_path, photo_path)
        # Далее можно провести необходимую обработку или отправить ответ пользователю
        await message.reply(f'Фотография сохранена: {photo_path}')


async def index_in_list(input_list, name: str):
    for nom_pos, element in enumerate(input_list, start = 0):
        if name == element:
            a = nom_pos
            return a


#тут идут кнопки вообще их нужно в отдельный

#эту часть кода можно перенести в файл с подобным функционалом
#тут продумана возможность расширения функционала


async def no_button(answer: str) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text=answer, callback_data=answer)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]]
    )
    return keyboard

async def navigate_photo_button(list_photo, now_photo: str):
    index = int(await index_in_list(list_photo, now_photo))
    button_page = InlineKeyboardButton(text=f"{index + 1}", callback_data="None")
    button_next= InlineKeyboardButton(text=">>", callback_data=f"next_{now_photo}")
    button_back=InlineKeyboardButton(text="<<", callback_data=f"back_{now_photo}")
    button_none=InlineKeyboardButton(text="  ", callback_data=f"None")
    if index==0 and len(list_photo)>index+1:
        return InlineKeyboardMarkup(
        inline_keyboard=[[button_none, button_page, button_next]]
    )
    elif index==0 and len(list_photo)==index+1:
        return 0
    elif len(list_photo)==index+1:
        return InlineKeyboardMarkup(
        inline_keyboard=[[button_back, button_page, button_none]]
    )
    else:
        return InlineKeyboardMarkup(
        inline_keyboard=[[button_back, button_page, button_next]]
    )

#тут основной ыункционал

@router.message(F.text == '/QR')
async def all_message(message: Message, state: FSMContext) -> None:
    logging.info(f'all_message {message.chat.id} / {message.text}')
    await message.answer(text='Пришлите логотип , ссылку и текст который будет под qr через _')
    await message.answer("Пример: https://example.com Scan Me!")
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
    logo_path = f"{const.save_folder}/{message.from_user.id}.png"
    await state.update_data(logo_path=logo_path)  # Сохраняем путь к лого в состоянии
    await message.answer(text="Если хотите ,чтобы под qr был текст отправьте его или нажмите на кнопку",
                         reply_markup=await no_button(answer="No")) #тут измените путь к функции если измените ее расположение
    await state.set_state(LinkQr.text_qr)



# 1. Исправленный обработчик для текста под QR
@router.message(StateFilter(LinkQr.text_qr))
async def handle_text_qr(message: Message, state: FSMContext) -> None:
    try:
        # Берем текст из сообщения, а не из подписи
        text = message.text or ""

        # Получаем данные из состояния
        state_data = await state.get_data()
        if not all(key in state_data for key in ['url', 'user_id', 'logo_path']):
            await message.answer("Ошибка: потеряны данные. Начните заново.")
            await state.clear()
            return

        # Создаем QR
        qr_path = await start_create_qr(
            url=state_data['url'],
            text=text,
            tg_id=state_data['user_id'],
            logo_path=state_data['logo_path']
        )

        # Отправляем фото
        await message.answer_photo(
            photo=FSInputFile(str(qr_path[0])),
            reply_markup=await navigate_photo_button(list_photo=qr_path, now_photo=str(qr_path[0]))
        )


    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        await message.answer("Произошла ошибка при создании QR"f"Ошибка: {str(e)}")
    finally:
        await state.clear()


# 2. Исправленный колбэк для кнопки "No"
@router.callback_query(F.data.startswith('No'))  # Изменили состояние!
async def handle_no_text(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        state_data = await state.get_data()

        if not all(key in state_data for key in ['url', 'user_id', 'logo_path']):
            await callback.message.answer("Ошибка: потеряны данные. Начните заново.")
            await state.clear()
            return

        qr_path = await start_create_qr(
            url=state_data['url'],
            text="",
            tg_id=state_data['user_id'],
            logo_path=state_data['logo_path']
        )
        await callback.message.answer_photo(
            photo=FSInputFile(str(qr_path[0])),
            reply_markup=await navigate_photo_button(list_photo = qr_path, now_photo=str(qr_path[0]))
        )


        await callback.answer()

    except Exception as e:
        logging.error(f"Ошибка в колбэке: {str(e)}")
        await callback.message.answer("Ошибка при создании QR")
    finally:
        await state.clear()


@router.callback_query(F.data.startswith('next_') | F.data.startswith('back_'))  # Изменили состояние!
async def handle_no_text(callback: CallbackQuery) -> None:
    data_parts = callback.data.split("_")
    qr_to_send=[]
    back_name = str(data_parts[1]).split("/")
    list_photo = await file_in_folder(folder_path=str(const.background_folder), extension=".png")
    for name in list_photo:
        name = str(name).split(".")
        qr_to_send.append(f"{name[0]}_{callback.from_user.id}.image")
    if "QR" in back_name:
        index =int(await index_in_list(input_list=list_photo, name=f"{back_name[1]}.png"))
    else:
        index =int(await index_in_list(input_list=list_photo, name=f"{back_name[0]}.png"))
    if data_parts[0] == 'back':
        await callback.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(f"{const.save_folder}/{str(qr_to_send[index-1]).replace('.png', '.image')}")),
            reply_markup=await navigate_photo_button(list_photo=qr_to_send, now_photo=qr_to_send[index-1]))
    else:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(f"{const.save_folder}/{str(qr_to_send[index+1]).replace('.png', '.image')}")),
            reply_markup=await navigate_photo_button(list_photo=qr_to_send, now_photo=qr_to_send[index + 1]))


