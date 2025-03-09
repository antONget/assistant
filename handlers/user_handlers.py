import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter, or_f
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import logging

from config_data.config import Config, load_config
from keyboards import user_keyboard as kb
from utils.error_handling import error_handler
from filter.filter import validate_russian_phone_number

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class Form(StatesGroup):
    description = State()
    file = State()
    contact = State()


@router.message(CommandStart())
@error_handler
async def process_start_command(message: Message, bot: Bot, state: FSMContext) -> None:
    """
    Старт бота
    :param message:
    :param bot:
    :param state:
    :return:
    """
    logging.info(f'process_start_command: {message.chat.id}')
    await state.set_state(state=None)
    await state.clear()
    await message.answer(text=f'👋 Приветствую!\n'
                              f'Чтобы заказать и/или узнать стоимость бота по вашему запросу, заполните заявку.\n'
                              f'❗️ Если у вас есть вопросы или чат-бот вам нужен срочно, свяжитесь со мной лично'
                              f' @AntonPon0marev.',
                         reply_markup=kb.create_order())
    if message.from_user.username:
        await state.update_data(username=message.from_user.username)
    else:
        await state.update_data(username='not_username')
    await bot.send_message(chat_id=config.tg_bot.admin_ids,
                           text=f'Пользователь @{message.from_user.username}/{message.from_user.id} запустил бота')
    await asyncio.sleep(60 * 60)
    data = await state.get_data()
    if not data.get('finish_dialog', False):
        await message.answer(text='Здравствуйте, вы запускали моего бота помощника для заказа разработки бота,'
                                  ' и не завершили оформление. У вас остались какие нибудь вопросы?'
                                  ' Готов на них ответить.')


@router.callback_query(F.data == 'create_order')
@error_handler
async def process_create_order(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """
    Старт бота
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_create_order: {callback.from_user.id}')
    dict_select = {"ТГ": 0, "ВК": 0, "WhatsApp": 0, "Avito": 0, "Discord": 0, "Одноклассники": 0}
    await state.update_data(dict_select=dict_select)
    await callback.message.edit_text(text=f'🎯 Разработка бота на какой площадке требуется? Можете выбрать несколько:',
                                     reply_markup=kb.select_platform(dict_select=dict_select))
    await callback.answer()


@router.callback_query(F.data.startswith('platform_'))
@error_handler
async def process_select_platform(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор нескольких платформ
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_select_platform: {callback.message.chat.id}')
    answer = callback.data.split('_')[-1]
    data = await state.get_data()
    dict_select = data['dict_select']
    if answer == 'continue':
        if not sum(list(dict_select.values())):
            await callback.answer(text='Выберите хотя бы одну платформу', show_alert=True)
            return
        else:
            await bot.delete_message(chat_id=callback.message.chat.id,
                                     message_id=callback.message.message_id)
            id_photo_1 = 'AgACAgIAAxkBAAIFhGcid9ofNfLpvSVZ9HpRgq3nzNNxAAIH5DEbAXsZSai24MioXBMjAQADAgADeAADNgQ'
            id_photo_2 = 'AgACAgIAAxkBAAIFhWcid-8vjnC1d0MxFuhFwjUc7J2EAALL5DEbWGQQSYmC3C17OLuxAQADAgADeAADNgQ'
            media = [InputMediaPhoto(media=id_photo_1), InputMediaPhoto(media=id_photo_2)]
            await callback.message.answer_media_group(media=media)
            await callback.message.answer(text='Какой способ реализации бота вы рассматриваете?',
                                          reply_markup=kb.keyboard_method())
    else:
        if dict_select[answer]:
            dict_select[answer] = 0
        else:
            dict_select[answer] = 1
        await state.update_data(dict_select=dict_select)
        await callback.message.edit_text(text=f'🎯 Разработка бота на какой площадке требуется?'
                                              f' Можете выбрать несколько:',
                                         reply_markup=kb.select_platform(dict_select=dict_select))
    await callback.answer()


@router.callback_query(F.data.startswith('method_'))
@error_handler
async def process_select_platform(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор нескольких платформ
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_select_platform: {callback.message.chat.id}')
    answer = callback.data.split('_')[-1]
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id - 1)
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id - 2)
    await state.update_data(method=answer)
    await callback.message.answer(text='Максимально подробно опишите,'
                                       ' какие у бота цели, и какой функционал в нём должен быть.')
    await state.set_state(Form.description)
    await callback.answer()


@router.message(StateFilter(Form.description))
@error_handler
async def get_task(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем описание задачи
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_task: {message.chat.id}')
    await state.update_data(description=message.text)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.answer(text="Есть ли у вас ТЗ (техническое задание, схема)?\n"
                              "Приложите фото или файл.",
                         reply_markup=kb.pass_tz())
    await state.set_state(Form.file)


@router.message(or_f(F.document, F.photo, F.text), StateFilter(Form.file))
@error_handler
async def process_material(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем материалы от пользователя
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_material: {message.chat.id}')
    if message.content_type == 'photo':
        photo = message.photo[-1]  # Получаем последнюю отправленную фотографию
        file_id = photo.file_id
        await state.update_data(photo_id=file_id)
    elif message.content_type == 'document':
        doc_id = message.document.file_id
        await state.update_data(doc_id=doc_id)
    else:
        await state.update_data(text_tz=message.text)
    await state.set_state(state=None)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.answer(text="У вас уже готовы все материалы для бота?"
                              " Или потребуется привлечение копирайтера/дизайнера и пр.?",
                         reply_markup=kb.keyboard_done())


@router.callback_query(F.data == 'pass_tz')
@error_handler
async def process_pass_tz(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пропуск добавления файлов
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_pass_tz: {callback.message.chat.id}')
    await state.update_data(text_tz="Не добавлено")
    await callback.message.edit_text(text="У вас уже готовы все материалы для бота?"
                                          " Или потребуется привлечение копирайтера/дизайнера и пр.?",
                                     reply_markup=kb.keyboard_done())


@router.callback_query(F.data.endswith('_done'))
@error_handler
async def process_finish(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_finish: {callback.message.chat.id}')
    await state.update_data(material=callback.data.split('_')[0])
    await state.update_data(finish_dialog=True)
    data = await state.get_data()
    if not data['username'] == 'not_username':

        if 'photo_id' in data:
            await bot.send_photo(chat_id=config.tg_bot.admin_ids,
                                 photo=data["photo_id"],
                                 caption=f'Для какой социальной сети нужен бот: {data["dict_select"]}\n'
                                         f'Способ разработки: {data["method"]}\n'
                                         f'Описание функционала бота: {data["description"]}\n'
                                         f'Материал для бота: {data["material"]}\n'
                                         f'Заказчик: <a href="tg://user?id={callback.from_user.username}">')
        elif 'doc_id' in data:
            await bot.send_document(chat_id=config.tg_bot.admin_ids,
                                    document=data['doc_id'],
                                    caption=f'Для какой социальной сети нужен бот: {data["dict_select"]}\n'
                                            f'Способ разработки: {data["method"]}\n'
                                            f'Описание функционала бота: {data["description"]}\n'
                                            f'Материал для бота: {data["material"]}\n'
                                            f'Заказчик: <a href="tg://user?id={callback.from_user.username}">')
        else:
            await bot.send_message(chat_id=config.tg_bot.admin_ids,
                                   text=f'Для какой социальной сети нужен бот: {data["dict_select"]}\n'
                                        f'Способ разработки: {data["method"]}\n'
                                        f'Описание функционала бота: {data["description"]}\n'
                                        f'Материал для бота: {data["material"]}\n'
                                        f'Техническое задание: {data["text_tz"]}\n'
                                        f'Заказчик: <a href="tg://user?id={callback.from_user.username}">')
        await callback.message.answer(text="🧑🏼‍💻Благодарю за ответы.\n"
                                           "Свяжусь с вами в ближайшее время.\n"
                                           "Работы, цены и советы по продвижению в моем ТГ канале:"
                                           " <a href='https://t.me/+1Qu1_h2OKGw3OTYy'>@GigabytesChatbots</a>\n")
    else:

        await callback.message.answer(text="В вашем профиле отсутствует username, пришлите мне контакт для связи",
                                      reply_markup=kb.keyboard_phone())
        await state.set_state(Form.contact)
    await callback.answer()


@router.message(or_f(F.text, F.contact), StateFilter(Form.contact))
@error_handler
async def process_validate_russian_phone_number(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем номер телефона пользователя (проводим его валидацию). Подтверждаем введенные данные
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info("process_validate_russian_phone_number")
    if message.contact:
        phone = str(message.contact.phone_number)
    else:
        phone = message.text
        if not validate_russian_phone_number(phone):
            await message.answer(text="Неверный формат номера. Повторите ввод, например 89991112222:")
            return
    await state.update_data(phone=phone)
    data = await state.get_data()
    await state.update_data(finish_dialog=True)
    if 'photo_id' in data:
        await bot.send_photo(chat_id=config.tg_bot.admin_ids,
                             photo=data["photo_id"],
                             caption=f'Для какой социальной сети нужен бот: {data["dict_select"]}\n'
                                     f'Способ разработки: {data["method"]}\n'
                                     f'Описание функционала бота: {data["description"]}\n'
                                     f'Материал для бота: {data["material"]}\n'
                                     f'Заказчик: <a href="tg://user?id={message.from_user.username}">\n'
                                     f'Телефон: {data["phone"]}')
    elif 'doc_id' in data:
        await bot.send_document(chat_id=config.tg_bot.admin_ids,
                                document=data['doc_id'],
                                caption=f'Для какой социальной сети нужен бот: {data["dict_select"]}\n'
                                        f'Способ разработки: {data["method"]}\n'
                                        f'Описание функционала бота: {data["description"]}\n'
                                        f'Техническое задание: {data["text_tz"]}\n'
                                        f'Материал для бота: {data["material"]}\n'
                                        f'Заказчик: <a href="tg://user?id={message.from_user.username}">\n'
                                        f'Телефон: {data["phone"]}')
    else:
        await bot.send_message(chat_id=config.tg_bot.admin_ids,
                               text=f'Для какой социальной сети нужен бот: {data["dict_select"]}\n'
                                    f'Способ разработки: {data["method"]}\n'
                                    f'Описание функционала бота: {data["description"]}\n'
                                    f'Материал для бота: {data["material"]}\n'
                                    f'Заказчик: <a href="tg://user?id={message.from_user.username}">\n'
                                    f'Телефон: {data["phone"]}')
    await message.answer(text="🧑🏼‍💻Благодарю за ответы.\n"
                              "Свяжусь с вами в ближайшее время.\n"
                              "Работы, цены и советы по продвижению в моем ТГ канале:"
                              " <a href='https://t.me/+1Qu1_h2OKGw3OTYy'>@GigabytesChatbots</a>\n")
