import os

import pytest

from .utils import new_image, execute_renamer


@pytest.fixture(scope='function')
def create_images_for_recursive(tmpdir) -> tuple:
    abs_temp_dir = tmpdir.mkdir('images')
    local_temp_dir_first_level = tmpdir.mkdir('images/level1')
    local_temp_dir_second_level = tmpdir.mkdir('images/level1/level2')

    filenames = (
        ('image1.jpg', '1001.01.01 01:01:01', 0o777),
        ('image2.jpg', '1002.01.01 01:01:01', 0o666),
        ('image3.jpg', '1003.01.01 01:01:01', 0o555),
        ('level1/imageR1.jpg', '2001.02.02 02:02:02', 0o777),
        ('level1/imageR2.jpg', '2002.02.02 02:02:02', 0o666),
        ('level1/imageR3.jpg', '2003.02.02 02:02:02', 0o555),
        ('level1/level2/imageL1.jpg', '3001.03.03 03:03:03', 0o777),
        ('level1/level2/imageL2.jpg', '3002.03.03 03:03:03', 0o666),
        ('level1/level2/imageL3.jpg', '3003.03.03 03:03:03', 0o555),
    )

    for file in filenames:
        new_image(abs_temp_dir, file[0], file[1], file[2])

    return abs_temp_dir, local_temp_dir_first_level, local_temp_dir_second_level


def test_recursive_default__zero_level__listdir(create_images_for_recursive: tuple):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    По-умолчанию, все директории, кроме самой первой, пропускаются и переименования не происходит.
    При пропуске директории ничего в консоль не выводится, поэтому проверки 'stdout' нет.
    """
    zero_level_dir, first_level_dir, second_level_dir = create_images_for_recursive
    execute_renamer(zero_level_dir)

    expected_list_of_images = sorted(['1001.01.01 01:01:01.jpg',
                                      '1002.01.01 01:01:01.jpg',
                                      '1003.01.01 01:01:01.jpg'])
    actual_list_of_images = os.listdir(zero_level_dir)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_recursive_default__first_level__listdir(create_images_for_recursive: tuple):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    По-умолчанию, все директории, кроме самой первой, пропускаются и переименования не происходит.
    При пропуске директории ничего в консоль не выводится, поэтому проверки 'stdout' нет.
    """
    zero_level_dir, first_level_dir, second_level_dir = create_images_for_recursive
    execute_renamer(zero_level_dir)

    expected_list_of_images = sorted(['imageR1.jpg',
                                      'imageR2.jpg',
                                      'imageR3.jpg'])
    actual_list_of_images = os.listdir(first_level_dir)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_recursive_default__second_level__listdir(create_images_for_recursive: tuple):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    По-умолчанию, все директории, кроме самой первой, пропускаются и переименования не происходит.
    При пропуске директории ничего в консоль не выводится, поэтому проверки 'stdout' нет.
    """
    zero_level_dir, first_level_dir, second_level_dir = create_images_for_recursive
    execute_renamer(zero_level_dir)

    expected_list_of_images = sorted(['imageL1.jpg',
                                      'imageL2.jpg',
                                      'imageL3.jpg'])
    actual_list_of_images = os.listdir(second_level_dir)
    for file in expected_list_of_images:
        assert file in actual_list_of_images


def test_recursive_false__zero_level__listdir(create_images_for_recursive: tuple):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    При флаге 'recursion = False' все директории, кроме самой первой, пропускаются и переименования не происходит.
    При пропуске директории ничего в консоль не выводится, поэтому проверки 'stdout' нет.
    """
    zero_level_dir, first_level_dir, second_level_dir = create_images_for_recursive
    execute_renamer(zero_level_dir, recursion=False)

    expected_list_of_images_second_level = sorted(['1001.01.01 01:01:01.jpg',
                                                   '1002.01.01 01:01:01.jpg',
                                                   '1003.01.01 01:01:01.jpg'])
    actual_list_of_images_second_level = os.listdir(zero_level_dir)
    for file in expected_list_of_images_second_level:
        assert file in actual_list_of_images_second_level


def test_recursive_false__first_level__listdir(create_images_for_recursive: tuple):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    При флаге 'recursion = False' все директории, кроме самой первой, пропускаются и переименования не происходит.
    При пропуске директории ничего в консоль не выводится, поэтому проверки 'stdout' нет.
    """
    zero_level_dir, first_level_dir, second_level_dir = create_images_for_recursive
    execute_renamer(zero_level_dir, recursion=False)

    expected_list_of_images_second_level = sorted(['imageR1.jpg',
                                                   'imageR2.jpg',
                                                   'imageR3.jpg'])
    actual_list_of_images_second_level = os.listdir(first_level_dir)
    for file in expected_list_of_images_second_level:
        assert file in actual_list_of_images_second_level


def test_recursive_false__second_level__listdir(create_images_for_recursive: tuple):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    При флаге 'recursion = False' все директории, кроме самой первой, пропускаются и переименования не происходит.
    При пропуске директории ничего в консоль не выводится, поэтому проверки 'stdout' нет.
    """
    zero_level_dir, first_level_dir, second_level_dir = create_images_for_recursive
    execute_renamer(zero_level_dir, recursion=False)

    expected_list_of_images_second_level = sorted(['imageL1.jpg',
                                                   'imageL2.jpg',
                                                   'imageL3.jpg'])
    actual_list_of_images_second_level = os.listdir(second_level_dir)
    for file in expected_list_of_images_second_level:
        assert file in actual_list_of_images_second_level


def test_recursive_true__zero_level__listdir(create_images_for_recursive: tuple):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    При флаге 'recursion' в значение 'True' все файлы в директориях должны быть переименованы.
    """
    zero_level_dir, first_level_dir, second_level_dir = create_images_for_recursive
    execute_renamer(zero_level_dir, recursion=True)

    expected_list_of_images_first_level = sorted(['1001.01.01 01:01:01.jpg',
                                                  '1002.01.01 01:01:01.jpg',
                                                  '1003.01.01 01:01:01.jpg'])
    actual_list_of_images_first_level = os.listdir(zero_level_dir)
    for file in expected_list_of_images_first_level:
        assert file in actual_list_of_images_first_level


def test_recursive_true__first_level__listdir(create_images_for_recursive: tuple):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    При флаге 'recursion' в значение 'True' все файлы в директориях должны быть переименованы.
    """
    zero_level_dir, first_level_dir, second_level_dir = create_images_for_recursive
    execute_renamer(zero_level_dir, recursion=True)

    expected_list_of_images_first_level = sorted(['2001.02.02 02:02:02.jpg',
                                                  '2002.02.02 02:02:02.jpg',
                                                  '2003.02.02 02:02:02.jpg'])
    actual_list_of_images_first_level = os.listdir(first_level_dir)
    for file in expected_list_of_images_first_level:
        assert file in actual_list_of_images_first_level


def test_recursive_true__second_level__listdir(create_images_for_recursive: tuple):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    При флаге 'recursion' в значение 'True' все файлы в директориях должны быть переименованы.
    """
    zero_level_dir, first_level_dir, second_level_dir = create_images_for_recursive
    execute_renamer(zero_level_dir, recursion=True)

    expected_list_of_images_first_level = sorted(['3001.03.03 03:03:03.jpg',
                                                  '3002.03.03 03:03:03.jpg',
                                                  '3003.03.03 03:03:03.jpg'])
    actual_list_of_images_first_level = os.listdir(second_level_dir)
    for file in expected_list_of_images_first_level:
        assert file in actual_list_of_images_first_level


def test_recursive_true__stdout(create_images_for_recursive: tuple, capsys):
    """
    Тестирует рекурсивное переименование файлов в директориях.
    При флаге 'recursion' в значение 'True' все файлы в директориях должны быть переименованы
    и должно появиться сообщение об этом.
    """
    zero_level_dir, first_level_dir, second_level_dir = create_images_for_recursive
    execute_renamer(zero_level_dir, recursion=True)
    expected_stdout = ['+ image1.jpg -> 1001.01.01 01:01:01.jpg',
                       '+ image2.jpg -> 1002.01.01 01:01:01.jpg',
                       '+ image3.jpg -> 1003.01.01 01:01:01.jpg',
                       '+ level1/imageR1.jpg -> level1/2001.02.02 02:02:02.jpg',
                       '+ level1/imageR2.jpg -> level1/2002.02.02 02:02:02.jpg',
                       '+ level1/imageR3.jpg -> level1/2003.02.02 02:02:02.jpg',
                       '+ level1/level2/imageL1.jpg -> level1/level2/3001.03.03 03:03:03.jpg',
                       '+ level1/level2/imageL2.jpg -> level1/level2/3002.03.03 03:03:03.jpg',
                       '+ level1/level2/imageL3.jpg -> level1/level2/3003.03.03 03:03:03.jpg']
    actual_stdout = capsys.readouterr()
    for out in expected_stdout:
        assert out in actual_stdout.out
