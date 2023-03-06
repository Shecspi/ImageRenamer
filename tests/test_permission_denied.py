import os

from .utils import execute_renamer, create_images


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
