import os
from pathlib import Path


async def rename_extension_to_image(file_path: str) -> str:
    """
    Физически переименовывает файл в файловой системе, меняя .png на .image

    :param file_path: Полный путь к файлу (например: '/path/to/file.png')
    :return: Новый путь к файлу после переименования
    :raises: FileNotFoundError, ValueError, RuntimeError
    """
    # Преобразуем путь в объект Path
    path = Path(file_path)

    # Проверяем существование файла
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    # Проверяем расширение
    #if path.suffix.lower() != '.png':
    #    raise ValueError(f"Файл должен иметь расширение .png, получено: {path.suffix}")

    # Формируем новый путь
    new_path = path.with_suffix('.image')

    # Проверяем, не существует ли файл с новым именем
    #if new_path.exists():
     #   raise FileExistsError(f"Файл уже существует: {new_path}")

    # Переименовываем файл
    try:
        path.rename(new_path)
        return str(new_path)
    except Exception as e:
        raise RuntimeError(f"Ошибка при переименовании: {e}")