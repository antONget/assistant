from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode
import random

def create_robust_qr(url, qr_size, logo_path=None, logo_max_size_ratio=0.15):
    # Создание QR-кода с повышенной устойчивостью
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Максимальная коррекция
        box_size=10,
        border=4,  # Увеличенная граница для защиты позиционных меток
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Генерация изображения
    img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')

    # Оптимизация контраста
    img = ImageOps.expand(img, border=2, fill='white')  # Дополнительная защитная рамка

    # Делаем чёрные части прозрачными
    data = img.getdata()
    new_data = [(0, 0, 0, 0) if item[:3] == (0, 0, 0) else (255, 255, 255, 255) for item in data]
    img.putdata(new_data)

    # Добавляем логотип с защитной подложкой
    if logo_path:
        try:
            logo = Image.open(logo_path).convert("RGBA")
            max_logo_size = int(qr_size * logo_max_size_ratio)

            # Создаем защитную подложку
            padding = int(max_logo_size * 0.1)  # 20% от размера логотипа
            bg_size = max_logo_size + padding * 2
            background = Image.new('RGBA', (bg_size, bg_size), (255, 255, 255, 255))

            # Масштабируем логотип
            logo.thumbnail((max_logo_size, max_logo_size))

            # Центрируем логотип на подложке
            logo_position = (
                (bg_size - logo.width) // 2,
                (bg_size - logo.height) // 2
            )
            background.paste(logo, logo_position, logo)

            # Позиционирование на QR-коде
            qr_position = (
                (img.width - bg_size) // 2,
                (img.height - bg_size) // 2
            )

            # Совмещаем слои
            img.paste(background, qr_position, background)

        except Exception as e:
            print(f"Ошибка при добавлении логотипа: {e}")

    return img.resize((qr_size, qr_size))


def create_text_layer(text, font_path, width, height):
    # Улучшенное позиционирование текста
    image = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(font_path, 72)
    except IOError:
        font = ImageFont.load_default()

    # Автоподбор размера шрифта
    for size in range(72, 12, -2):
        font = ImageFont.truetype(font_path, size)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        if text_width < width * 0.9:
            break

    # Центрирование с учетом базовой линии
    ascent, descent = font.getmetrics()
    text_width = font.getlength(text)
    x = (width - text_width) / 2
    y = (height - (ascent + descent)) / 2 - descent

    mask = Image.new("L", (width, height), 255)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((x, y), text, fill=0, font=font)

    image.putalpha(mask)
    return image

def crop_square(image_path, output_path, left, top, width, height):
    """
    Вырезает квадрат из изображения по заданным координатам.

    :param image_path: Путь к исходному изображению.
    :param output_path: Путь для сохранения обрезанного изображения.
    :param left: Координата X верхнего левого угла квадрата.
    :param top: Координата Y верхнего левого угла квадрата.
    :param size: Размер стороны квадрата.
    """
    # Открываем изображение
    img = Image.open(image_path)

    # Проверяем, что координаты и размер квадрата не выходят за пределы изображения
    if left < 0 or top < 0 or left + width > img.width or top + height > img.height:
        raise ValueError("Координаты или размер квадрата выходят за пределы изображения.")

    # Вырезаем квадрат
    cropped_img = img.crop((left, top, left + width, top + height))

    # Сохраняем результат
    cropped_img.save(output_path)
    print(f"Квадрат успешно вырезан и сохранён в {output_path}")

async def start_create_qr(url: str, tg_id: int, logo_path: str, text: str = ""):
    # Параметры
    qr_size = 600  # Увеличенный размер для лучшего качества
    text_height = 120 # Динамическая высота текста
    font_path = "arial_bolditalicmt.ttf"

    # Генерация QR-кода
    qr_image = create_robust_qr(
        url=url,
        qr_size=qr_size,
        logo_path=logo_path,
        logo_max_size_ratio=0.10
    )

    # Создаем базовое изображение
    if text != "":
        final_image = Image.new("RGBA", (qr_size, qr_size + text_height), (0, 0, 0, 0))
    else:
        final_image = Image.new("RGBA", (qr_size, qr_size ), (0, 0, 0, 0))
    final_image.paste(qr_image, (0, 0))

    # Генерация текста только если он есть
    if text:
        text_image = create_text_layer(text, font_path, qr_size, text_height)
        final_image.paste(text_image, (0, qr_size))

    # Сохранение результата
    final_image.save(f"{tg_id}.png")
    put = await start_crop(path_qr=f"{tg_id}.png")
    return put

async def start_crop(path_qr: str ,path_background: str = "background.png"):
    # Открываем прозрачный QR-код
    qr_img = Image.open(path_qr)
    width, height = qr_img.size

    # Открываем фоновое изображение
    background = Image.open(path_background)# тут еще переменная
    width_back, height_back = background.size

    low_limit= 0
    upper_limit_x= width_back - width
    upper_limit_y= height_back - height

    random_x= random.randint(low_limit, upper_limit_x)
    random_y= random.randint(low_limit, upper_limit_y)


    # Накладываем QR-код на фон
    background.paste(qr_img, (random_x, random_y), qr_img)  # (x, y) — координаты размещения


    # Сохраняем результат
    background.save(path_qr)#как то изъебнуться

    crop_square(
        image_path=path_qr,
        output_path=path_qr,
        left=random_x,
        top=random_y,
        width=width,
        height=height
    )
    background.save(f"QR/{path_qr}")
    return path_qr