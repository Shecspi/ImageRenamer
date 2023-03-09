import os

import pytest
import piexif

from PIL import Image

from src import ImageRenamer


@pytest.fixture(scope='function')
def create_images(tmpdir) -> str:
    temp_dir = tmpdir.mkdir('images')

    filenames = (
        ('image1.jpg', '2023.01.06 10:00:37', 0o777),  # Нормально переименовывается
        ('image2.jpg', '2000.01.06 10:00:37', 0o666),  # Нормально переименовывается
        ('image3.jpg', '1900.01.06 10:00:37', 0o555),  # Нормально переименовывается
        ('image4.jpg', '1800.01.06 10:00:37', 0o400),  # Нормально переименовывается
        ('image5.jpg', '1999.01.06 22:33:44', 0o377),  # Отказано в доступе
        ('image6.jpg', '2011.01.06 10:00:37', 0o777),  # Test: File already exists
        ('image7.jpg', '2011.01.06 10:00:37', 0o777),  # Test: File already exists
        ('image8.jpg', '2222.11.22 11:22:33', 0o777),  # Test: File already exists
        ('image9.jpg', '2011.01.06 10:00:37', 0o777),  # Test: File already exists
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


@pytest.fixture(scope='function')
def create_recoursive_folder(tmpdir):
    temp_dir = tmpdir.mkdir('images/recoursive')
    temp_dir_level2 = tmpdir.mkdir('images/recoursive/level2')

    filenames = (
        ('imageR1.jpg', '1111.11.11 11:22:33', 0o777),
        ('imageR2.jpg', '2222.01.01 10:00:37', 0o666),
        ('imageR3.jpg', '3333.05.05 10:00:37', 0o555),
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

    for file in filenames:
        # Создание файла изображения
        image = Image.new('RGB', (10, 10), 'blue')
        filename = temp_dir_level2.join(file[0])
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


def execute_renamer(temp_dir: str,
                    template: str = '%Y.%m.%d %H:%M:%S',
                    make_unique_name: bool = False,
                    recursion: bool = False) -> None:
    """
    Запускает ImageRenamer.
    """
    renamer = ImageRenamer.ImageRenamer(temp_dir)
    renamer.set_template(template)
    renamer.set_make_unique_name(make_unique_name)
    renamer.set_recursion(recursion)
    renamer.rename()


def new_image(abs_path: str, filename: str,
              datetime_string: str, chmod: oct):
    # Создание файла изображения
    image = Image.new('RGB', (10, 10), 'blue')
    filename = abs_path.join(filename)
    image.save(str(filename), 'JPEG')

    # Внесение даты и времени создания в EXIF
    exif_dict = piexif.load(str(filename))
    new_datetime = datetime_string
    exif_dict['0th'][piexif.ImageIFD.DateTime] = new_datetime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_datetime
    exif_dict['Exif'][36867] = new_datetime
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, str(filename))

    os.chmod(filename, chmod)
