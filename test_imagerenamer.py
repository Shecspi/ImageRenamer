import os

import pytest
import piexif

from PIL import Image

from src import ImageRenamer


@pytest.fixture(scope='function')
def create_images(tmpdir_factory) -> str:
    temp_dir = tmpdir_factory.mktemp('images')

    filenames = (
        ('image1.jpg', '2023.01.06 10:00:37', 0o777),  # Нормально переименовывается
        ('image2.jpg', '2000.01.06 10:00:37', 0o666),  # Нормально переименовывается
        ('image3.jpg', '1900.01.06 10:00:37', 0o555),  # Нормально переименовывается
        ('image4.jpg', '1800.01.06 10:00:37', 0o400),  # Нормально переименовывается
        ('image5.jpg', '1999.01.06 22:33:44', 0o377),  # Отказано в доступе
        ('image6.jpg', '2011.01.06 10:00:37', 0o777),  # Нормально переименуется
        ('image7.jpg', '2011.01.06 10:00:37', 0o777),  # Не переименуется, файл уже существует
    )

    for file in filenames:
        # Создание файла изображения
        image = Image.new('RGB', (10, 10), 'blue')
        filename = temp_dir.join(file[0])
        image.save(str(filename), 'JPEG')

        # Внесение даты и времени создания в EXIF
        exif_dict = piexif.load(str(filename))
        new_datetime = file[1]
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_datetime
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_datetime
        exif_dict['Exif'][36867] = new_datetime
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, str(filename))

        os.chmod(filename, file[2])

    return temp_dir


def execute_renamer(temp_dir: str, template: str = '%Y.%m.%d %H:%M:%S') -> None:
    """
    Запускает ImageRenamer.
    """
    renamer = ImageRenamer.ImageRenamer()
    renamer.set_path(temp_dir)
    renamer.set_template(template)
    renamer.rename()


def test_correct_rename__listdir(create_images: str):
    """
    Тестирует корректное переименование файлов.
    """
    execute_renamer(create_images)
    expected_list_of_images = sorted(['2023.01.06 10:00:37.jpg', '2000.01.06 10:00:37.jpg',
                                      '1900.01.06 10:00:37.jpg', '1800.01.06 10:00:37.jpg'])
    actual_list_of_images = os.listdir(create_images)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_correct_rename__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль при корректном переименовании файлов.
    """
    execute_renamer(create_images)
    expected_stdout = ['+ image1.jpg -> 2023.01.06 10:00:37.jpg', '+ image2.jpg -> 2000.01.06 10:00:37.jpg',
                       '+ image3.jpg -> 1900.01.06 10:00:37.jpg', '+ image4.jpg -> 1800.01.06 10:00:37.jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_same_datetimes__listdir(create_images: str):
    """
    Тестирует отсутствие переименования файлов, в случае двух одинаковых имён файлов.
    """
    execute_renamer(create_images)
    expected_list_of_images = sorted(['2011.01.06 10:00:37.jpg', 'image7.jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_same_datetimes__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль, в случае двух одинаковых имён файлов.
    """
    execute_renamer(create_images)
    expected_stdout = ['+ image6.jpg -> 2011.01.06 10:00:37.jpg',
                       '- image7.jpg невозможно переименовать, 2011.01.06 10:00:37.jpg уже существует.']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_permission_denied__listdir(create_images: str):
    """
    Тестирует отсутствие переименования файлов, в случае остутствия прав доступа к файлу.
    """
    execute_renamer(create_images)
    expected_list_of_images = sorted(['2023.01.06 10:00:37.jpg', '1800.01.06 10:00:37.jpg',
                                      'image5.jpg', '2011.01.06 10:00:37.jpg'])
    actual_list_of_images = sorted(os.listdir(create_images))
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_permission_denied__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль, в случае остутствия прав доступа к файлу.
    """
    execute_renamer(create_images)
    expected_stdout = ['+ image1.jpg -> 2023.01.06 10:00:37.jpg', '+ image4.jpg -> 1800.01.06 10:00:37.jpg',
                       '- image5.jpg невозможно переименовать. Отказано в доступе.',
                       '+ image6.jpg -> 2011.01.06 10:00:37.jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_users_template__listdir(create_images: str):
    """
    Тестирует переименование файлов, в случае изменения шаблона для имён файлов.
    """
    execute_renamer(create_images, '%Y%m%d_%H%M%S')
    expected_list_of_images = sorted(['20230106_100037.jpg', '20000106_100037.jpg',
                                      '19000106_100037.jpg', '18000106_100037.jpg'])
    actual_list_of_images = os.listdir(create_images)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_users_template__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль, в случае изменения шаблона для имён файлов.
    """
    execute_renamer(create_images, '%Y%m%d_%H%M%S')
    expected_stdout = ['+ image1.jpg -> 20230106_100037.jpg', '+ image2.jpg -> 20000106_100037.jpg',
                       '+ image3.jpg -> 19000106_100037.jpg', '+ image4.jpg -> 18000106_100037.jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out


def test_file_doesnt_have_exif__listdir(create_images: str):
    """
    Тестирует отсутствие переименования, в случае обработки файла без EXIF-данных.
    """
    image = Image.new('RGB', (10, 10), 'blue')
    image.save(str(create_images + '/image_without_exif.jpg'), 'JPEG')
    execute_renamer(create_images)

    expected_list_of_images = 'image_without_exif.jpg'
    actual_list_of_images = os.listdir(create_images)
    assert expected_list_of_images in actual_list_of_images


def test_file_doesnt_have_exif__stdout(create_images: str, capsys):
    """
    Тестирует вывод в консоль, в случае обработки файла без EXIF-данных.
    """
    image = Image.new('RGB', (10, 10), 'blue')
    image.save(str(create_images + '/image_without_exif.jpg'), 'JPEG')
    execute_renamer(create_images)

    expected_stdout = '- image_without_exif.jpg невозможно переименовать. У файла нет EXIF-данных.'
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out
