from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def create_order() -> InlineKeyboardMarkup:
    """
    Стартавая клавиатура для создания заявки
    :return:
    """
    logging.info('select_platform')
    button_1 = InlineKeyboardButton(text='Заполнить заявку',
                                    callback_data='create_order')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard


def select_platform(dict_select: dict) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком платформ и множественным выбором
    :return:
    """
    logging.info('select_platform')
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for key, value in dict_select.items():
        callback = f'platform_{key}'
        flag_select = ""
        if value:
            flag_select = "✅ "
        buttons.append(InlineKeyboardButton(
            text=f'{flag_select}{key}',
            callback_data=callback))
    button_company = InlineKeyboardButton(
        text='ПРОДОЛЖИТЬ >>',
        callback_data='platform_continue')
    kb_builder.row(*buttons, width=3)
    kb_builder.row(button_company, width=1)
    return kb_builder.as_markup()


def keyboard_method() -> InlineKeyboardMarkup:
    """
    Выбор метода реализации бота
    :return:
    """
    logging.info('keyboard_method')
    button_1 = InlineKeyboardButton(text='Конструктор',
                                    callback_data='method_Конструктор')
    button_2 = InlineKeyboardButton(text='Python',
                                    callback_data='method_Python')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2]],
    )
    return keyboard


def pass_tz() -> InlineKeyboardMarkup:
    """
    Стартавая клавиатура для создания заявки
    :return:
    """
    logging.info('pass_tz')
    button_1 = InlineKeyboardButton(text='Пропустить',
                                    callback_data='pass_tz')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard


def keyboard_done() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Всё готово!',
                                    callback_data='all_done')
    button_2 = InlineKeyboardButton(text='Частично',
                                    callback_data='part_done')
    button_3 = InlineKeyboardButton(text='Потребуется помощь специалистов',
                                    callback_data='None_done')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2], [button_3]],
    )
    return keyboard


def keyboard_phone() -> ReplyKeyboardMarkup:
    logging.info(f'keyboard_phone')
    button_1 = KeyboardButton(text='Поделиться ☎️', request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1]], resize_keyboard=True
    )
    return keyboard
