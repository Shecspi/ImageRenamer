import os

from .utils import execute_renamer, create_images


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
