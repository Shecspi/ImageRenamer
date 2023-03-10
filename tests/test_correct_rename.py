import os

import pytest

from .utils import new_image, add_exif, execute_renamer


@pytest.fixture(scope='function', name='create_images')
def fixture_create_images(tmpdir) -> str:
    """
    Фикстура, срабатывающая при каждом вызове тестирующей функции.
    Создаёт все необходимые для тестирования папки и файлы.
    :param tmpdir: Фикстура, указывающая на временную папку, в которой будут создаваться файлы.
    :return: Абсолютный адрес временной папки, в которой были созданы файлы.
    """
    abs_temp_dir = tmpdir.mkdir('images')

    filenames = (
        ('file_exists1.jpg', '1001.01.01 01:01:01'),
        ('file_exists2.jpg', '1002.01.01 01:01:01'),
        ('file_exists3.jpg', '1003.01.01 01:01:01'),
        ('file_exists4.jpg', '1004.01.01 01:01:01'),
    )

    for file in filenames:
        new_image(abs_temp_dir, file[0])
        try:
            add_exif(abs_temp_dir, file[0], file[1])
        except IndexError:
            ...
    return str(abs_temp_dir)


def test_correct_rename__listdir(create_images: str):
    """
    Тестирует корректное переименование файлов.
    """
    execute_renamer(create_images)
    expected_list_of_images = sorted(['10010101_010101.jpg', '10020101_010101.jpg',
                                      '10030101_010101.jpg', '10040101_010101.jpg'])
    actual_list_of_images = os.listdir(create_images)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_correct_rename__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль при корректном переименовании файлов.
    """
    execute_renamer(create_images)
    expected_stdout = ['+ file_exists1.jpg -> 10010101_010101.jpg',
                       '+ file_exists2.jpg -> 10020101_010101.jpg',
                       '+ file_exists3.jpg -> 10030101_010101.jpg',
                       '+ file_exists4.jpg -> 10040101_010101.jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out
