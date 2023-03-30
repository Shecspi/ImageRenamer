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
        ('users_template1.jpg', '1001.01.01 01:01:01'),
        ('users_template2.jpg', '1002.01.01 01:01:01'),
        ('users_template3.jpg', '1003.01.01 01:01:01'),
    )

    for file in filenames:
        new_image(abs_temp_dir, file[0])
        add_exif(abs_temp_dir, file[0], file[1])

    return str(abs_temp_dir)


def test_users_template_1__listdir(create_images: str):
    """
    Тестирует переименование файлов, в случае изменения шаблона для имён файлов.
    """
    execute_renamer(create_images, '%Y%m%d-%H%M%S')
    expected_list_of_images = sorted(['10010101-010101.jpg', '10020101-010101.jpg',
                                      '10030101-010101.jpg'])
    actual_list_of_images = os.listdir(create_images)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_users_template_1__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль, в случае изменения шаблона для имён файлов.
    """
    execute_renamer(create_images, '%Y%m%d-%H%M%S')
    expected_stdout = ['[  OK  ]  users_template1.jpg -> 10010101-010101.jpg',
                       '[  OK  ]  users_template2.jpg -> 10020101-010101.jpg',
                       '[  OK  ]  users_template3.jpg -> 10030101-010101.jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_users_template_2__listdir(create_images: str):
    """
    Тестирует переименование файлов, в случае изменения шаблона для имён файлов.
    """
    execute_renamer(create_images, '%Y-%m-%d_%H-%M-%S')
    expected_list_of_images = sorted(['1001-01-01_01-01-01.jpg', '1002-01-01_01-01-01.jpg',
                                      '1003-01-01_01-01-01.jpg'])
    actual_list_of_images = os.listdir(create_images)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_users_template_2__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль, в случае изменения шаблона для имён файлов.
    """
    execute_renamer(create_images, '%Y-%m-%d_%H-%M-%S')
    expected_stdout = ['[  OK  ]  users_template1.jpg -> 1001-01-01_01-01-01.jpg',
                       '[  OK  ]  users_template2.jpg -> 1002-01-01_01-01-01.jpg',
                       '[  OK  ]  users_template3.jpg -> 1003-01-01_01-01-01.jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_users_template_3__listdir(create_images: str):
    """
    Тестирует переименование файлов, в случае изменения шаблона для имён файлов.
    """
    execute_renamer(create_images, 'Год %Y Месяц %m День %d_%H-%M-%S')
    expected_list_of_images = sorted(['Год 1001 Месяц 01 День 01_01-01-01.jpg',
                                      'Год 1002 Месяц 01 День 01_01-01-01.jpg',
                                      'Год 1003 Месяц 01 День 01_01-01-01.jpg'])
    actual_list_of_images = os.listdir(create_images)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_users_template_3__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль, в случае изменения шаблона для имён файлов.
    """
    execute_renamer(create_images, 'Год %Y Месяц %m День %d_%H-%M-%S')
    expected_stdout = ['[  OK  ]  users_template1.jpg -> Год 1001 Месяц 01 День 01_01-01-01.jpg',
                       '[  OK  ]  users_template2.jpg -> Год 1002 Месяц 01 День 01_01-01-01.jpg',
                       '[  OK  ]  users_template3.jpg -> Год 1003 Месяц 01 День 01_01-01-01.jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out
