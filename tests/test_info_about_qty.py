import os

import pytest

from .utils import new_image, add_exif, execute_renamer


@pytest.fixture(scope='function', name='create_images_success',
                params=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
def fixture_create_images_success(tmpdir, request) -> str:
    abs_temp_dir = tmpdir.mkdir(f'images{str(request.param)}')
    for iteration in range(0, request.param + 1):
        new_image(abs_temp_dir, f'with_exif{iteration}.jpg')
        try:
            add_exif(abs_temp_dir, f'with_exif{iteration}.jpg', f'100{iteration}.01.01 01:01:01')
        except IndexError:
            ...
    return str(abs_temp_dir)


@pytest.fixture(scope='function', name='create_images_failed',
                params=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
def fixture_create_images_failed(tmpdir, request) -> str:
    abs_temp_dir = tmpdir.mkdir(f'images{str(request.param)}')
    for iteration in range(0, request.param + 1):
        new_image(abs_temp_dir, f'with_exif{iteration}.jpg')
        try:
            add_exif(abs_temp_dir, f'with_exif{iteration}.jpg', f'Incorrect exif-data')
        except IndexError:
            ...
    return str(abs_temp_dir)


def test_info_about_success__stdout(create_images_success: str, capsys):
    """
    Тестирует вывод в консоль сообщения о количестве переименнованных и непереименнованных файлов.
    """
    execute_renamer(create_images_success)
    expected_stdout = [
        'Успешно переименовано: 1 файл',
        'Успешно переименовано: 2 файла',
        'Успешно переименовано: 3 файла',
        'Успешно переименовано: 4 файла',
        'Успешно переименовано: 5 файлов',
        'Успешно переименовано: 6 файлов',
        'Успешно переименовано: 7 файлов',
        'Успешно переименовано: 8 файлов',
        'Успешно переименовано: 9 файлов',
        'Успешно переименовано: 10 файлов'
    ]
    iteration = int(create_images_success.split(os.sep)[-1][6:7])
    actual_stdout = capsys.readouterr()
    assert expected_stdout[iteration] in actual_stdout.out


def test_info_about_failed__stdout(create_images_failed: str, capsys):
    """
    Тестирует вывод в консоль сообщения о количестве переименнованных и непереименнованных файлов.
    """
    execute_renamer(create_images_failed)
    expected_stdout = [
        'Не удалось переименовать: 1 файл',
        'Не удалось переименовать: 2 файла',
        'Не удалось переименовать: 3 файла',
        'Не удалось переименовать: 4 файла',
        'Не удалось переименовать: 5 файлов',
        'Не удалось переименовать: 6 файлов',
        'Не удалось переименовать: 7 файлов',
        'Не удалось переименовать: 8 файлов',
        'Не удалось переименовать: 9 файлов',
        'Не удалось переименовать: 10 файлов'
    ]
    iteration = int(create_images_failed.split(os.sep)[-1][6:7])
    actual_stdout = capsys.readouterr()
    assert expected_stdout[iteration] in actual_stdout.out
