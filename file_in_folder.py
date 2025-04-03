from pathlib import Path


async def get_files_by_extension(folder_path, extension):
    """
    Возвращает список файлов с указанным расширением в заданной папке.

    :param folder_path: Путь к целевой папке
    :param extension: Расширение файлов (с точкой или без, например 'txt' или '.txt')
    :return: Список имён файлов
    """
    folder = Path(folder_path)

    # Нормализуем расширение (добавляем точку и переводим в нижний регистр)
    extension = extension.lower().lstrip('.')
    target_suffix = f".{extension}"

    # Собираем файлы
    return [
        file.name
        for file in folder.iterdir()
        if file.is_file() and file.suffix.lower() == target_suffix
    ]

