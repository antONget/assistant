from aiogram import Bot
from config_data.config import Config, load_config

config: Config = load_config()


async def send_message_admins(bot: Bot, text: str):
    """
    Рассылка сообщения администраторам
    :param bot:
    :param text:
    :return:
    """
    list_admins = config.tg_bot.admin_ids.split(',')
    for admin in list_admins:
        try:
            await bot.send_message(chat_id=admin,
                                   text=text)
        except:
            pass