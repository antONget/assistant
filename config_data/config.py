from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
    admin_ids: str       # Список id администраторов бота
    support_id: int

@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               support_id=env('SUPPORT_ID'),
                               admin_ids=env('ADMIN_IDS')))


@dataclass
class Constant:
    background_folder: str
    font_path: str
    short_background_folder: str
    download: str
    save_folder: str


def load_constant(path: str = None) -> Constant:
    env = Env()
    env.read_env(path)
    return Constant(
        background_folder=env('BACKGRAUND_FOLDER'),
        font_path=env('FONT_PATH'),
        short_background_folder=env('SHORT_BACKGRAUND_FOLDER'),
        download=env('DOWNLOADS_FOLDER'),
        save_folder=env('SAVE_FOLDER')
    )

