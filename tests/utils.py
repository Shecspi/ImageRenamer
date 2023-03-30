import os

import pytest
import piexif
import settings

from PIL import Image

from src import ImageRenamer


def execute_renamer(temp_dir: str,
                    template: str = settings.TEMPLATE,
                    make_unique_name: bool = settings.UNIQUE_NAME,
                    recursion: bool = settings.RECURSION) -> None:
    """
    Запускает ImageRenamer.
    """
    renamer = ImageRenamer.ImageRenamer(temp_dir)
    renamer.set_template(template)
    renamer.set_make_unique_name(make_unique_name)
    renamer.set_recursion(recursion)
    renamer.rename()


def new_image(abs_path: str, filename: str):
    # Создание файла изображения
    image = Image.new('RGB', (10, 10), 'blue')
    filename = abs_path.join(filename)
    image.save(str(filename), 'JPEG')


def add_exif(abs_path: str, filename: str, datetime_string: str):
    filename = abs_path.join(filename)
    exif_dict = piexif.load(str(filename))
    new_datetime = datetime_string
    exif_dict['0th'][piexif.ImageIFD.DateTime] = new_datetime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_datetime
    exif_dict['Exif'][36867] = new_datetime
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, str(filename))


def change_chmod(abs_path: str, filename: str, chmod: oct):
    filename = abs_path.join(filename)
    os.chmod(filename, chmod)
