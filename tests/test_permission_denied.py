import os

import pytest

from .utils import new_image, add_exif, execute_renamer, change_chmod


@pytest.fixture(scope='function')
def create_images(tmpdir) -> tuple:
    abs_temp_dir = tmpdir.mkdir('images')

    filenames = (
        ('permissions1.jpg', '1001.01.01 01:01:01', 0o777),
        ('permissions2.jpg', '1002.01.01 01:01:01', 0o666),
        ('permissions3.jpg', '1003.01.01 01:01:01', 0o400),
        ('permission_denied.jpg', '1004.01.01 01:01:01', 0o377)
    )

    for file in filenames:
        new_image(abs_temp_dir, file[0])
        add_exif(abs_temp_dir, file[0], file[1])
        change_chmod(abs_temp_dir, file[0], file[2])

    return abs_temp_dir


def test_permission_denied__listdir(create_images: str):
    """
    Тестирует отсутствие переименования файлов, в случае остутствия прав доступа к файлу.
    """
    execute_renamer(create_images)
    expected_list_of_images = sorted(['10010101_010101.jpg', '10020101_010101.jpg',
                                      '10030101_010101.jpg', 'permission_denied.jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_permission_denied__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль, в случае остутствия прав доступа к файлу.
    """
    execute_renamer(create_images)
    expected_stdout = ['+ permissions1.jpg -> 10010101_010101.jpg',
                       '+ permissions2.jpg -> 10020101_010101.jpg',
                       '+ permissions3.jpg -> 10030101_010101.jpg',
                       '- permission_denied.jpg невозможно переименовать. Отказано в доступе.']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out
