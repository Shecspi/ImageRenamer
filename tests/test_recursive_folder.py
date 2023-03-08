import os

from .utils import execute_renamer, create_images, create_recoursive_folder


def test_recursive_folder_correct_rename__listdir(create_images: str, create_recoursive_folder: str):
    """
    Тестирует вывод в консоль при корректном переименовании файлов при рекурсивном обходе папок.
    """
    execute_renamer(create_images)
    expected_list_of_images = sorted(['1111.11.11 11:22:33.jpg',
                                      '2222.01.01 10:00:37.jpg',
                                      '3333.05.05 10:00:37.jpg'])
    actual_list_of_images = os.listdir(create_recoursive_folder)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_recursive_folder_correct_rename__stdout(create_images: str, create_recoursive_folder: str, capsys):
    """
    Тестирует вывод в консоль при корректном переименовании файлов при рекурсивном обходе папок.
    """
    execute_renamer(create_images)
    expected_stdout = ['+ recoursive/imageR1.jpg -> recoursive/1111.11.11 11:22:33.jpg',
                       '+ recoursive/imageR2.jpg -> recoursive/2222.01.01 10:00:37.jpg',
                       '+ recoursive/imageR3.jpg -> recoursive/3333.05.05 10:00:37.jpg',
                       '+ recoursive/level2/imageR1.jpg -> recoursive/level2/1111.11.11 11:22:33.jpg',
                       '+ recoursive/level2/imageR2.jpg -> recoursive/level2/2222.01.01 10:00:37.jpg',
                       '+ recoursive/level2/imageR3.jpg -> recoursive/level2/3333.05.05 10:00:37.jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out
