from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, File
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
import logging
import asyncio
import os
from config_data.config import Config, load_config
from aiogram.types.input_file import FSInputFile

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()
user_dict = dict()


class Form(StatesGroup):
    description = State()
    file = State()
    video2 = State()
    paper2 = State()
    video3 = State()
    paper3 = State()
    finish = State()


@router.message(CommandStart())
async def process_start_command(message: Message) -> None:
    logging.info(f'process_start_command: {message.chat.id}')
    await message.answer(text="""👋 Приветствую!
Чтобы заказать и/или узнать стоимость бота по вашему запросу, ответьте на несколько вопросов ниже.
❗️ Если у вас останутся вопросы или чат-бот вам нужен срочно, свяжитесь со мной лично @AntonPon0marev сразу после ответов.
""")
    await asyncio.sleep(10)
    button_1 = InlineKeyboardButton(text='ВК',
                                    callback_data='vk_data')
    button_2 = InlineKeyboardButton(text='Телеграм',
                                    callback_data='tg_data')
    button_3 = InlineKeyboardButton(text='Whatsapp',
                                    callback_data='wp_data')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2, button_3]],
    )
    await message.answer(text="🎯 Разработку бот на какой площадке требуется?",
                         reply_markup=keyboard)


@router.callback_query(F.data.endswith('_data'))
async def process_description(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_description: {callback.message.chat.id}')
    await state.update_data(social=callback.data.split('_')[0])
    # users_dict[callback.message.chat.id]['social'] = F.data.split('_')[0]
    await callback.message.answer(text="""Для заказа максимально подробно опишите:
Цели использования бота и функционал, который в нём должен быть.
""")
    await state.set_state(Form.description)


@router.message(StateFilter(Form.description))
async def process_file(message: Message, state: FSMContext) -> None:
    logging.info(f'process_file: {message.chat.id}')
    await state.update_data(description=message.text)
    # users_dict[message.chat.id]['description'] = message.text
    await message.answer(text="""Есть ли у вас ТЗ (техническое задание, схема)?
Приложите файл.
""")
    await state.set_state(Form.file)


# @router.message(F.photo)
# async def advanced_handler(message: Message, bot: Bot):
#     if message.content_type == 'photo':
#         photo = message.photo[-1]  # Получаем последнюю отправленную фотографию
#         file_id = photo.file_id
#         file = await bot.get_file(file_id)
#         file_path = file.file_path
#         save_path = os.path.join('data', f'{message.chat.id}-{file_id}.jpg')
#         await bot.download_file(file_path, save_path)


@router.message((F.document | F.photo | F.text), StateFilter(Form.file))
async def process_material(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_material: {message.chat.id}')
    if message.content_type == 'photo':
        photo = message.photo[-1]  # Получаем последнюю отправленную фотографию
        file_id = photo.file_id
        await state.update_data(photo_id=file_id)
        file = await bot.get_file(file_id)
        file_path = file.file_path
        save_path = os.path.join('data', f'{message.chat.id}-{file_id}.jpeg')
        await bot.download_file(file_path, save_path)
    elif message.content_type == 'text':
        await state.update_data(text_tz=message.text)
    else:
        doc = message.document
        file_name = doc.file_name
        file_ext = os.path.splitext(file_name)[1]
        file_path = os.path.join('data/', f"{message.chat.id}-{file_name}")
        await state.update_data(path_document=file_path)
        await bot.download(doc.file_id, file_path)

    button_1 = InlineKeyboardButton(text='Все готово!',
                                    callback_data='all_done')
    button_2 = InlineKeyboardButton(text='Частично',
                                    callback_data='part_done')
    button_3 = InlineKeyboardButton(text='Потребуется помощь специалистов',
                                    callback_data='None_done')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2, button_3]],
    )
    await message.answer(text="""У вас уже готовы все материалы для бота? Или потребуется привлечение копирайтера/дизайнера и пр.?
""",
                         reply_markup=keyboard)


@router.callback_query(F.data.endswith('_done'))
async def process_finish(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_finish: {callback.message.chat.id}')
    await state.update_data(material=callback.data.split('_')[0])
    user_dict[callback.message.chat.id] = await state.get_data()
    print(user_dict)
    # await callback.message.answer(text=f'Для какой социальной сети нужен бот: {user_dict[callback.message.chat.id]["social"]}\n'
    #                                    f'Описание функционала бота: {user_dict[callback.message.chat.id]["description"]}\n'
    #                                    f'Материал для бота: {user_dict[callback.message.chat.id]["material"]}')
    if 'photo_id' in user_dict[callback.message.chat.id]:
        await bot.send_photo(chat_id=config.tg_bot.admin_ids,
                             photo=user_dict[callback.message.chat.id]["photo_id"],
                             caption=f'Для какой социальной сети нужен бот: {user_dict[callback.message.chat.id]["social"]}\n'
                                     f'Описание функционала бота: {user_dict[callback.message.chat.id]["description"]}\n'
                                     f'Материал для бота: {user_dict[callback.message.chat.id]["material"]}')
    elif 'text_tz' in user_dict[callback.message.chat.id]:
        await bot.send_message(chat_id=config.tg_bot.admin_ids,
                               text=f'Для какой социальной сети нужен бот: {user_dict[callback.message.chat.id]["social"]}\n'
                                    f'Описание функционала бота: {user_dict[callback.message.chat.id]["description"]}\n'
                                    f'Техническое задание: {user_dict[callback.message.chat.id]["text_tz"]}\n'
                                    f'Материал для бота: {user_dict[callback.message.chat.id]["material"]}')
    else:
        await bot.send_message(chat_id=config.tg_bot.admin_ids,
                               text=f'Для какой социальной сети нужен бот: {user_dict[callback.message.chat.id]["social"]}\n'
                                    f'Описание функционала бота: {user_dict[callback.message.chat.id]["description"]}\n'
                                    f'Материал для бота: {user_dict[callback.message.chat.id]["material"]}')
        document = FSInputFile(f'{user_dict[callback.message.chat.id]["path_document"]}')
        await bot.send_document(chat_id=config.tg_bot.admin_ids,
                                document=document)
    await callback.message.answer(text="""🧑🏼‍💻Благодарю за ответы.  Свяжусь с вами в ближайшее время.
А пока подписывайтесь на мой канал: <a href='https://t.me/GigabytesChatbots'>@GigabytesChatbots</a>
Работы, цены, разборы и советы по продвижению в ТГ.""")

