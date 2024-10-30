from aiogram import Router
from aiogram.types import Message, CallbackQuery
from config_data.config import Config, load_config

import logging

router = Router()
config: Config = load_config()


@router.callback_query()
async def all_callback(callback: CallbackQuery) -> None:
    logging.info(f'all_callback: {callback.message.chat.id} / {callback.data}')
    await callback.message.answer(text='Я вас не понимаю!')
    await callback.answer()


@router.message()
async def all_message(message: Message) -> None:
    logging.info(f'all_message {message.chat.id} / {message.text}')
    if message.photo:
        logging.info(f'all_message message.photo')
        print(message.photo[-1].file_id)
        return

    if message.video:
        logging.info(f'all_message message.photo')
        print(message.video.file_id)
        return

    if message.sticker:
        logging.info(f'all_message message.sticker')
        return