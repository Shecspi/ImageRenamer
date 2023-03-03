import os
import io
import sys

import pytest
import piexif

from PIL import Image

from src import ImageRenamer


def create_images(datetimes: list, temp_dir: str) -> None:
    for item in range(0, len(datetimes)):
        # Создание файла изображения
        image = Image.new('RGB', (10, 10), 'blue')
        filename = temp_dir.join(f'image{item}.jpg')
        image.save(str(filename))

        # Внесение даты и времени создания в EXIF
        exif_dict = piexif.load(str(filename))
        new_datetime = datetimes[item]
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_datetime
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_datetime
        exif_dict['Exif'][36867] = new_datetime
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, str(filename))


@pytest.fixture(scope='function')
def different_template_of_datetime_in_exif(tmpdir_factory):
    datetimes = sorted([
        '2023.01.06 10:00:37', '2000/01/06 10:00:37'
    ])
    temp_dir = tmpdir_factory.mktemp('images')
    create_images(datetimes, temp_dir)

    return temp_dir

@pytest.fixture(scope='function')
def same_datetimes_for_two_files(tmpdir_factory):
    datetimes = sorted([
        '2023.01.06 10:00:37', '2023.01.06 10:00:37'
    ])
    temp_dir = tmpdir_factory.mktemp('images')
    create_images(datetimes, temp_dir)

    return temp_dir


def execute_renamer(temp_dir):
    renamer = ImageRenamer.ImageRenamer()
    renamer.set_path(temp_dir)
    renamer.set_template('%Y%m%d %H:%M:%S')
    renamer.rename()


def test_correct_rename(different_template_of_datetime_in_exif, capsys):
    """
    Проверяет на корректность прочтения различных форматов даты и времени, а также на переименование файлов.
    Также проверяет корректность вывода в консоль.
    """
    execute_renamer(different_template_of_datetime_in_exif)

    expected_list_of_images = sorted(['20230106 10:00:37.jpg', '20000106 10:00:37.jpg'])
    actual_list_of_images = os.listdir(different_template_of_datetime_in_exif)

    expected_stdout = ['+ image0.jpg -> 20000106 10:00:37.jpg', '+ image1.jpg -> 20230106 10:00:37.jpg']
    actual_stdout = capsys.readouterr()

    for out in expected_stdout:
        assert out in actual_stdout.out
    assert expected_list_of_images == actual_list_of_images


def test_same_datetimes_for_two_files(same_datetimes_for_two_files, capsys):
    """
    Проверяет, что два файла с одинаковыми датой и временем в EXIF, не создадутся.
    Переименоваться должен только один, а у второго должно отобразиться сообщение об ошибке.
    """
    execute_renamer(same_datetimes_for_two_files)

    expected_list_of_images = sorted(['20230106 10:00:37.jpg', 'image1.jpg'])
    actual_list_of_images = sorted(os.listdir(same_datetimes_for_two_files))

    expected_stdout = '- image1.jpg невозможно переименовать, 20230106 10:00:37.jpg уже существует.'
    actual_stdout = capsys.readouterr().out

    assert expected_list_of_images == actual_list_of_images
    assert expected_stdout in actual_stdout
