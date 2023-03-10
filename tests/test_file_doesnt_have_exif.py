import os

import pytest

from .utils import new_image, add_exif, execute_renamer


@pytest.fixture(scope='function')
def create_images(tmpdir) -> tuple:
    abs_temp_dir = tmpdir.mkdir('images')

    filenames = (
        ('without_exif1.jpg',),  # Файл без EXIF
        ('without_exif2.jpg', ''),  # EXIF есть, но Datetime не заполнен
        ('without_exif3.jpg', 'incorrect Datetime info'),  # Некорректные данные в EXIF
        ('without_exif4.jpg', '1001.22.22 01:01:01'),  # Некорректные данные в EXIF (такой даты не может быть)
    )

    for file in filenames:
        new_image(abs_temp_dir, file[0])
        try:
            add_exif(abs_temp_dir, file[0], file[1])
        except IndexError:
            ...

    return abs_temp_dir


def test_file_doesnt_have_exif__listdir(create_images: str):
    """
    Тестирует отсутствие переименования, в случае обработки файла без EXIF-данных.
    """
    execute_renamer(create_images)
    expected_list_of_images = ['without_exif1.jpg', 'without_exif2.jpg', 'without_exif3.jpg', 'without_exif4.jpg']
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_file_doesnt_have_exif__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль, в случае обработки файла без EXIF-данных.
    """
    execute_renamer(create_images)
    expected_stdout = ['- without_exif1.jpg невозможно переименовать. У файла нет EXIF-данных.',
                       '- without_exif2.jpg невозможно переименовать. Не получилось прочитать EXIF-данные.',
                       '- without_exif3.jpg невозможно переименовать. Не получилось прочитать EXIF-данные.',
                       '- without_exif4.jpg невозможно переименовать. Не получилось прочитать EXIF-данные.']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out
