import os

from PIL import Image

from .utils import execute_renamer, create_images


def test_file_already_exists_unique_names_default__listdir(create_images: str):
    """
    Тестируем что будет, если уже существует файл с таким же названием, в которое должно быть переименовано изображение.
    По-умолчанию --make-unique-name принимает значение False.
    В таком случае переименование не должно осуществиться.
    """
    image = Image.new('RGB', (10, 10), 'blue')
    image.save(str(create_images + '/2222.11.22 11:22:33.jpg'), 'JPEG')
    execute_renamer(create_images)

    expected_list_of_images = 'image8.jpg'
    actual_list_of_images = os.listdir(create_images)
    assert expected_list_of_images in actual_list_of_images


def test_file_already_exists_unique_names_default__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если уже существует файл с таким же названием, в которое должно быть переименовано изображение.
    По-умолчанию --make-unique-name принимает значение False.
    В таком случае переименование не должно осуществиться.
    """
    image = Image.new('RGB', (10, 10), 'blue')
    image.save(str(create_images + '/2222.11.22 11:22:33.jpg'), 'JPEG')
    execute_renamer(create_images)

    expected_stdout = '- image8.jpg невозможно переименовать, 2222.11.22 11:22:33.jpg уже существует.'
    actual_stdout = capsys.readouterr()
    assert expected_stdout in actual_stdout.out



def test_file_already_exists_unique_names_false__listdir(create_images: str):
    """
    Тестируем что будет, если уже существует файл с таким же названием, в которое должно быть переименовано изображение.
    Устанавливаем --make-unique-name в значение False.
    В таком случае переименование не должно осуществиться.
    """
    image = Image.new('RGB', (10, 10), 'red')
    image.save(str(create_images + '/2222.11.22 11:22:33.jpg'), 'JPEG')
    execute_renamer(create_images, make_unique_name=False)

    expected_list_of_images = 'image8.jpg'
    actual_list_of_images = os.listdir(create_images)
    assert expected_list_of_images in actual_list_of_images


def test_file_already_exists_unique_names_false__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если уже существует файл с таким же названием, в которое должно быть переименовано изображение.
    Устанавливаем --make-unique-name в значение False.
    В таком случае переименование не должно осуществиться.
    """
    image = Image.new('RGB', (10, 10), 'red')
    image.save(str(create_images + '/2222.11.22 11:22:33.jpg'), 'JPEG')
    execute_renamer(create_images, make_unique_name=False)

    expected_stdout = '- image8.jpg невозможно переименовать, 2222.11.22 11:22:33.jpg уже существует.'
    actual_stdout = capsys.readouterr()
    assert expected_stdout in actual_stdout.out


def test_file_already_exists_unique_names_true__listdir(create_images: str):
    """
    Тестируем что будет, если уже существует файл с таким же названием, в которое должно быть переименовано изображение.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован, но с добавлением суффикса ' (copy)'.
    """
    image = Image.new('RGB', (10, 10), 'red')
    image.save(str(create_images + '/2222.11.22 11:22:33.jpg'), 'JPEG')
    execute_renamer(create_images, make_unique_name=True)

    expected_list_of_images = '2222.11.22 11:22:33 (copy).jpg'
    actual_list_of_images = os.listdir(create_images)
    assert expected_list_of_images in actual_list_of_images


def test_file_already_exists_unique_names_true__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если уже существует файл с таким же названием, в которое должно быть переименовано изображение.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован, но с добавлением суффикса ' (copy)'.
    """
    image = Image.new('RGB', (10, 10), 'red')
    image.save(str(create_images + '/2222.11.22 11:22:33.jpg'), 'JPEG')
    execute_renamer(create_images, make_unique_name=True)

    expected_stdout = '+ image8.jpg -> 2222.11.22 11:22:33 (copy).jpg'
    actual_stdout = capsys.readouterr()
    assert expected_stdout in actual_stdout.out


def test_same_datetimes_unique_names_default__listdir(create_images: str):
    """
    Тестируем что будет, если файл с таким же названием, в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    По-умолчанию --make-unique-name принимает значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images)
    expected_list_of_images = sorted(['2011.01.06 10:00:37.jpg', 'image7.jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_same_datetimes_unique_names_default__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если файл с таким же названием, в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    По-умолчанию --make-unique-name принимает значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images)
    expected_stdout = ['+ image6.jpg -> 2011.01.06 10:00:37.jpg',
                       '- image7.jpg невозможно переименовать, 2011.01.06 10:00:37.jpg уже существует.']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_same_datetimes_unique_names_false__listdir(create_images: str):
    """
    Тестируем что будет, если файл с таким же названием, в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    Устанавливаем --make-unique-name в значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images, make_unique_name=False)
    expected_list_of_images = sorted(['2011.01.06 10:00:37.jpg', 'image7.jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_same_datetimes_unique_names_false__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если файл с таким же названием, в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    Устанавливаем --make-unique-name в значение False.
    В таком случае переименование не должно осуществиться.
    """
    execute_renamer(create_images, make_unique_name=False)
    expected_stdout = ['+ image6.jpg -> 2011.01.06 10:00:37.jpg',
                       '- image7.jpg невозможно переименовать, 2011.01.06 10:00:37.jpg уже существует.']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_same_datetimes_unique_names_true__listdir(create_images: str):
    """
    Тестируем что будет, если файл с таким же названием, в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован, но с добавлением суффикса ' (copy)'.
    """
    execute_renamer(create_images, make_unique_name=True)
    expected_list_of_images = sorted(['2011.01.06 10:00:37.jpg', '2011.01.06 10:00:37 (copy).jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images
    print(os.listdir(create_images))


def test_same_datetimes_unique_names_true__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если файл с таким же названием, в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован, но с добавлением суффикса ' (copy)'.
    """
    execute_renamer(create_images, make_unique_name=True)
    expected_stdout = ['+ image6.jpg -> 2011.01.06 10:00:37.jpg',
                       '+ image7.jpg -> 2011.01.06 10:00:37 (copy).jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_same_datetimes_unique_names_true_recursive__listdir(create_images: str):
    """
    Тестируем что будет, если файл с таким же названием, в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы, а также появился файл с суффиксом ' (copy)'.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован, но с добавлением двойного суффикса ' (copy) (copy)'.
    """
    execute_renamer(create_images, make_unique_name=True)
    expected_list_of_images = sorted(['2011.01.06 10:00:37.jpg', '2011.01.06 10:00:37 (copy).jpg',
                                      '2011.01.06 10:00:37 (copy) (copy).jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_same_datetimes_unique_names_true_recursive__stdout(create_images: str, capsys):
    """
    Тестируем что будет, если файл с таким же названием, в которое должно быть переименовано изображение,
    изначально не существовал, но появился в процессе работы программы, а также появился файл с суффиксом ' (copy)'.
    Устанавливаем --make-unique-name в значение True.
    В таком случае файл должен быть переименован, но с добавлением двойного суффикса ' (copy) (copy)'.
    """
    execute_renamer(create_images, make_unique_name=True)
    expected_stdout = ['+ image6.jpg -> 2011.01.06 10:00:37.jpg',
                       '+ image7.jpg -> 2011.01.06 10:00:37 (copy).jpg',
                       '+ image9.jpg -> 2011.01.06 10:00:37 (copy) (copy).jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out
