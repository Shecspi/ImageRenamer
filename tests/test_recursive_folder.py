import os

from .utils import execute_renamer, create_images, create_recoursive_folder


def test_recursive_folder_correct_rename_defaualt__listdir(create_images: str, create_recoursive_folder: str):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    По-умолчанию, все директории пропускаются и переименования не происходит.
    При пропуске директории ничего в консоль не выводится, поэтому проверки 'stdout' нет.
    """
    execute_renamer(create_images)
    expected_list_of_images = sorted(['imageR1.jpg',
                                      'imageR2.jpg',
                                      'imageR3.jpg'])
    actual_list_of_images = os.listdir(create_recoursive_folder)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_recursive_folder_correct_rename_false__listdir(create_images: str, create_recoursive_folder: str):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    При флаге recursion в значение False все директории пропускаются и переименования не происходит.
    При пропуске директории ничего в консоль не выводится, поэтому проверки 'stdout' нет.
    """
    execute_renamer(create_images, recursion=False)
    expected_list_of_images = sorted(['imageR1.jpg',
                                      'imageR2.jpg',
                                      'imageR3.jpg'])
    actual_list_of_images = os.listdir(create_recoursive_folder)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_recursive_folder_correct_rename_true__listdir(create_images: str, create_recoursive_folder: str):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    При флаге 'recursion' в значение 'True' все файлы в директориях должны быть переименованы.
    """
    execute_renamer(create_images, recursion=True)
    expected_list_of_images = sorted(['1111.11.11 11:22:33.jpg',
                                      '2222.01.01 10:00:37.jpg',
                                      '3333.05.05 10:00:37.jpg'])
    actual_list_of_images = os.listdir(create_recoursive_folder)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_recursive_folder_correct_rename_true__stdout(create_images: str, create_recoursive_folder: str, capsys):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    При флаге 'recursion' в значение 'True' все файлы в директориях должны быть переименованы
    и должно появиться сообщение об этом.
    """
    execute_renamer(create_images, recursion=True)
    expected_stdout = ['+ recoursive/imageR1.jpg -> recoursive/1111.11.11 11:22:33.jpg',
                       '+ recoursive/imageR2.jpg -> recoursive/2222.01.01 10:00:37.jpg',
                       '+ recoursive/imageR3.jpg -> recoursive/3333.05.05 10:00:37.jpg',
                       '+ recoursive/level2/imageR1.jpg -> recoursive/level2/1111.11.11 11:22:33.jpg',
                       '+ recoursive/level2/imageR2.jpg -> recoursive/level2/2222.01.01 10:00:37.jpg',
                       '+ recoursive/level2/imageR3.jpg -> recoursive/level2/3333.05.05 10:00:37.jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out
