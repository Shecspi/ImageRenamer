import os

from .utils import execute_renamer, create_images


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
