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
        ('10010101_010101.jpg',),
        ('file_exists1.jpg', '1001.01.01 01:01:01'),
        ('file_exists2.jpg', '1002.01.01 01:01:01'),
        ('file_exists3.jpg', '1002.01.01 01:01:01'),
        ('file_exists4.jpg', '1002.01.01 01:01:01'),
        ('file_exists5.jpg', '1002.01.01 01:01:01'),
    )

    for file in filenames:
        new_image(abs_temp_dir, file[0])
        try:
            add_exif(abs_temp_dir, file[0], file[1])
        except IndexError:
            ...
    return str(abs_temp_dir)


def test_file_already_exists_unique_names_default__listdir(create_images: str):
    """
    Тестируем что будет, если уже существует файл с таким же названием,
    в которое должно быть переименовано изображение.
    По-умолчанию --make-unique-name принимает значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images)
    expected_list_of_images = 'file_exists1.jpg'
    actual_list_of_images = os.listdir(create_images)
    assert expected_list_of_images in actual_list_of_images


def test_file_already_exists_unique_names_default__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если уже существует файл с таким же названием,
    в которое должно быть переименовано изображение.
    По-умолчанию --make-unique-name принимает значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images)
    expected_stdout = ('[ FAIL ] file_exists1.jpg невозможно переименовать, '
                       '10010101_010101.jpg уже существует.')
    actual_stdout = capsys.readouterr()
    assert expected_stdout in actual_stdout.out


def test_file_already_exists_unique_names_false__listdir(create_images: str):
    """
    Тестируем что будет, если уже существует файл с таким же названием,
    в которое должно быть переименовано изображение.
    Устанавливаем --make-unique-name в значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images, make_unique_name=False)

    expected_list_of_images = 'file_exists1.jpg'
    actual_list_of_images = os.listdir(create_images)
    assert expected_list_of_images in actual_list_of_images


def test_file_already_exists_unique_names_false__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если уже существует файл с таким же названием,
    в которое должно быть переименовано изображение.
    Устанавливаем --make-unique-name в значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images, make_unique_name=False)
    expected_stdout = ('[ FAIL ] file_exists1.jpg невозможно переименовать, '
                       '10010101_010101.jpg уже существует.')
    actual_stdout = capsys.readouterr()
    assert expected_stdout in actual_stdout.out


def test_file_already_exists_unique_names_true__listdir(create_images: str):
    """
    Тестируем что будет, если уже существует файл с таким же названием,
    в которое должно быть переименовано изображение.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован, но с добавлением суффикса ' (copy)'.
    """
    execute_renamer(create_images, make_unique_name=True)
    expected_list_of_images = '10010101_010101 (copy).jpg'
    actual_list_of_images = os.listdir(create_images)
    assert expected_list_of_images in actual_list_of_images


def test_file_already_exists_unique_names_true__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если уже существует файл с таким же названием,
    в которое должно быть переименовано изображение.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован, но с добавлением суффикса ' (copy)'.
    """
    execute_renamer(create_images, make_unique_name=True)
    expected_stdout = '[  OK  ] file_exists1.jpg -> 10010101_010101 (copy).jpg'
    actual_stdout = capsys.readouterr()
    assert expected_stdout in actual_stdout.out


def test_same_datetimes_unique_names_default__listdir(create_images: str):
    """
    Тестируем что будет, если файл с таким же названием,
    в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    По-умолчанию --make-unique-name принимает значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images)
    expected_list_of_images = sorted(['10020101_010101.jpg', 'file_exists3.jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_same_datetimes_unique_names_default__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если файл с таким же названием,
    в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    По-умолчанию --make-unique-name принимает значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images)
    expected_stdout = [
        '[  OK  ] file_exists2.jpg -> 10020101_010101.jpg',
        '[ FAIL ] file_exists3.jpg невозможно переименовать, 10020101_010101.jpg уже существует.'
    ]
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_same_datetimes_unique_names_false__listdir(create_images: str):
    """
    Тестируем что будет, если файл с таким же названием,
    в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    Устанавливаем --make-unique-name в значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images, make_unique_name=False)
    expected_list_of_images = sorted(['10020101_010101.jpg', 'file_exists3.jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_same_datetimes_unique_names_false__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если файл с таким же названием,
    в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    Устанавливаем --make-unique-name в значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images, make_unique_name=False)
    expected_stdout = [
        '[  OK  ] file_exists2.jpg -> 10020101_010101.jpg',
        '[ FAIL ] file_exists3.jpg невозможно переименовать, 10020101_010101.jpg уже существует.'
    ]
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_same_datetimes_unique_names_true__listdir(create_images: str):
    """
    Тестируем что будет, если файл с таким же названием,
    в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован, но с добавлением суффикса ' (copy)'.
    """
    execute_renamer(create_images, make_unique_name=True)
    expected_list_of_images = sorted(['10020101_010101.jpg', '10020101_010101 (copy).jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_same_datetimes_unique_names_true__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если файл с таким же названием,
    в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован, но с добавлением суффикса ' (copy)'.
    """
    execute_renamer(create_images, make_unique_name=True)
    expected_stdout = [
        '[  OK  ] file_exists2.jpg -> 10020101_010101.jpg',
        '[  OK  ] file_exists3.jpg -> 10020101_010101 (copy).jpg'
    ]
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_same_datetimes_unique_names_true_recursive__listdir(create_images: str):
    """
    Тестируем что будет, если файл с таким же названием,
    в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы,
    а также появился файл с суффиксом ' (copy)'.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован,
    но с добавлением двойного суффикса ' (copy) (copy)'.
    """
    execute_renamer(create_images, make_unique_name=True)
    expected_list_of_images = sorted(['10020101_010101.jpg', '10020101_010101 (copy).jpg',
                                      '10020101_010101 (copy) (copy).jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_same_datetimes_unique_names_true_recursive__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если файл с таким же названием,
    в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы,
    а также появился файл с суффиксом ' (copy)'.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован,
    но с добавлением двойного (тройного и т.д.) суффикса ' (copy) (copy)'.
    """
    execute_renamer(create_images, make_unique_name=True)
    expected_stdout = [
        '[  OK  ] file_exists2.jpg -> 10020101_010101.jpg',
        '[  OK  ] file_exists3.jpg -> 10020101_010101 (copy).jpg',
        '[  OK  ] file_exists4.jpg -> 10020101_010101 (copy) (copy).jpg',
        '[  OK  ] file_exists5.jpg -> 10020101_010101 (copy) (copy) (copy).jpg'
    ]
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out
