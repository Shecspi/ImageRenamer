import os
from os.path import isfile
from datetime import datetime
from exif import Image
from plum.exceptions import UnpackError


class Rename:
    # Формат даты и времени, по которому извлекается информация из EXIF.
    # В моих фотографиях он именно такой, но не исключаю, что в других фотоаппаратах может отличаться.
    standart_format_of_datetime: str = '%Y:%m:%d %H:%M:%S'

    # Шаблон для нового имени файла
    template_datetime: str = '%Y-%m-%d %H-%M-%S'

    result_code: dict = {
        'SUCCESS': '+ "{0}" успешно переименован в "{1}"',
        'FILE_EXISTS': '- "{0}" не переименован, так как "{1}" уже существует.',
        'PERMISSION_DENIED': '- "{0}" не переименован. Отказано в доступе.',
        'FILE_DOESNT_HAVE_EXIF': '- "{0}" не переименован. У файла нет EXIF-данных.',
        'INCORRECT_EXIF': '- "{0}" не переименова. У файла некорректные EXIF-данные.',
        'CANT_UNPACK': '- "{0}" не переименован. Не получилось распаковать файл.'
    }

    def __init__(self):
        for filename in sorted(os.listdir()):
            if isfile(filename):
                try:
                    new_name = self._get_datetime_from_exif(filename)
                except ValueError:
                    self._show_result(self.result_code['INCORRECT_EXIF_CODE'], filename)
                    continue
                except PermissionError:
                    self._show_result(self.result_code['PERMISSION_DENIED'], filename)
                    continue
                except UnpackError:
                    self._show_result(self.result_code['CANT_UNPACK'], filename)
                    continue

                if new_name:
                    try:
                        self._rename_file(filename, new_name)
                        self._show_result(self.result_code['SUCCESS'], filename, new_name)
                    except FileExistsError:
                        self._show_result(self.result_code['FILE_EXISTS'], filename, new_name)
                    except PermissionError:
                        self._show_result(self.result_code['PERMISSION_DENIED'], filename)
                else:
                    self._show_result(self.result_code['FILE_DOESNT_HAVE_EXIF'], filename)

    def _show_result(self, code: str, old_filename: str, new_filename: str = ''):
        """
        Выводит в консоль сообщение с результатом переименования файла.
        """
        print(code.format(old_filename, new_filename))

    def _get_datetime_from_exif(self, filename: str) -> str | bool:
        """
        Пытается получить EXIF-данные из файла, указанного в 'filename'.
        В случае успеха - возвращает форматированную строку, пригодную для нового имени файла.
        Если EXIF-информации у файла нет, возвращает False.

        В случае, если формат даты и времени в EXIF не соответствует стандартному, вызывается исключение ValueError.
        """
        image = Image(filename)
        extension = filename.split('.')[-1]

        if image.has_exif:
            old_format = datetime.strptime(image.datetime_original, self.standart_format_of_datetime)

            return self._reformat_datetime(old_format) + f'.{extension}'

        return False

    def _reformat_datetime(self, old_format: datetime) -> str:
        """
        Возвращает строку с изменённым на основе шаблона форматом даты и времени.
        """
        return datetime.strftime(old_format, self.template_datetime)

    def _rename_file(self, old_name: str, new_name: str):
        """
        Переименовывает файл 'old_name' в 'new_name'.
        В случае, если файл с именем 'new_name' уже существует, возвращает исключение FileExistsError.
        """
        if isfile(new_name):
            raise FileExistsError

        os.rename(old_name, new_name)
