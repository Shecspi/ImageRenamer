import os
import io
import sys

import pytest
import piexif

from PIL import Image

from src import ImageRenamer


@pytest.fixture(scope='function')
def temp_dir(tmpdir_factory):
    datetimes = sorted([
        '2023.01.06 10:00:37', '2000/01/06 10:00:37'
    ])
    tmpdir = tmpdir_factory.mktemp('images')
    for item in range(0, len(datetimes)):
        # Создание файла изображения
        image = Image.new('RGB', (10, 10), 'blue')
        filename = tmpdir.join(f'image{item}.jpg')
        image.save(str(filename))

        # Внесение даты и времени создания в EXIF
        exif_dict = piexif.load(str(filename))
        new_datetime = datetimes[item]
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_datetime
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_datetime
        exif_dict['Exif'][36867] = new_datetime
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, str(filename))

    return tmpdir


def execute_renamer(temp_dir):
    renamer = ImageRenamer.ImageRenamer()
    renamer.set_path(temp_dir)
    renamer.set_template('%Y%m%d %H:%M:%S')
    renamer.rename()


def test_rename(temp_dir):
    """ Проверка на корректность прочтения различных форматов даты и времени, а также на переименование файлов. """
    execute_renamer(temp_dir)
    expected_list_of_images = sorted(['20230106 10:00:37.jpg', '20000106 10:00:37.jpg'])
    actual_list_of_images = os.listdir(temp_dir)
    assert expected_list_of_images == actual_list_of_images


def test_stdout(temp_dir, capsys):
    """ Проверка вывода в консоль. """
    execute_renamer(temp_dir)
    captured = capsys.readouterr()
    assert '-> 20230106 10:00:37.jpg' in captured.out
