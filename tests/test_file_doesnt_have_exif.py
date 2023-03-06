import os

from PIL import Image

from .utils import execute_renamer, create_images


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
