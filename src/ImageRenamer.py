import os
from os.path import isfile, isdir
from datetime import datetime

import click
from exif import Image
from plum.exceptions import UnpackError


class ImageRenamer:
    """
    Производит переименование всех файлов в текущем каталоге на основе информации из EXIF-данных.
    Директории пропускаются, рекурсивное переименование директорий не поддерживается.
    """
    # Формат даты и времени, по которому извлекается информация из EXIF.
    # В моих фотографиях он именно такой, но не исключаю, что в других фотоаппаратах может отличаться.
    standart_format_of_datetime: str = '%Y:%m:%d %H:%M:%S'

    # Шаблон для нового имени файла
    template_datetime: str = '%Y-%m-%d %H-%M-%S'

    result_code: dict = {
        'SUCCESS': (click.style('+ ', fg='green') +
                    click.style('{0}', bold=True, fg='green') +
                    click.style(' -> ', fg='green') +
                    click.style('{1}', bold=True, fg='green')),
        'FILE_EXISTS': (click.style('- ', fg='yellow') +
                        click.style('{0}', bold=True, fg='yellow') +
                        click.style(' невозможно переименовать, ', fg='yellow') +
                        click.style('{1}', bold=True, fg='yellow') +
                        click.style(' уже существует.', fg='yellow')),
        'PERMISSION_DENIED': (click.style('- ', fg='red') +
                              click.style('{0}', bold=True, fg='red') +
                              click.style(' невозможно переименовать. Отказано в доступе.', fg='red')),
        'FILE_DOESNT_HAVE_EXIF': (click.style('- ', fg='red') +
                                  click.style('{0}', bold=True, fg='red') +
                                  click.style(' невозможно переименовать. У файла нет EXIF-данных.', fg='red')),
        'INCORRECT_EXIF': (click.style('- ', fg='red') +
                           click.style('{0}', bold=True, fg='red') +
                           click.style(' невозможно переименовать. У файла некорректные EXIF-данные.', fg='red')),
        'CANT_UNPACK': (click.style('- ', fg='red') +
                        click.style('{0}', bold=True, fg='red') +
                        click.style(' невозможно переименовать. Не получилось распаковать файл.', fg='red'))
    }

    def rename(self, preview: bool = False) -> None:
        """
        :param preview: Если True, то будет выведен виртуальный результат переименования, но без переименования.
        :return: None
        """
        for filename in sorted(os.listdir()):
            if isdir(filename):
                continue

            new_name = self.__check_availability_to_file(filename)
            if new_name in self.result_code.values():
                self.__print_message(new_name, filename)
                continue

            if new_name is not None:
                if isfile(new_name):
                    self.__print_message(self.result_code['FILE_EXISTS'], filename, new_name)
                    continue

                if not preview:
                    try:
                        os.rename(filename, new_name)
                    except PermissionError:
                        self.__print_message(self.result_code['PERMISSION_DENIED'], filename)
                self.__print_message(self.result_code['SUCCESS'], filename, new_name)
            else:
                self.__print_message(self.result_code['FILE_DOESNT_HAVE_EXIF'], filename)

    def __check_availability_to_file(self, filename) -> str | None:
        """
        Пытается получить EXIF-данные из файла.
        Если файл не содержит EXIF-данных, то возвращает None.
        В случае успеха возвращает строку str, содержащую новое имя для файла.
        Если произошло исключение, то возвращает строку str с кодом ошибки.
        """
        try:
            result = self.__get_datetime_from_exif(filename)
        except ValueError:
            result = self.result_code['INCORRECT_EXIF_CODE']
        except PermissionError:
            result = self.result_code['PERMISSION_DENIED']
        except UnpackError:
            result = self.result_code['CANT_UNPACK']

        return result

    def __get_datetime_from_exif(self, filename: str) -> str | None:
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

            return self.__reformat_datetime(old_format) + f'.{extension}'

        return None

    def __reformat_datetime(self, old_format: datetime) -> str:
        """
        Возвращает строку с изменённым на основе шаблона форматом даты и времени.
        """
        return datetime.strftime(old_format, self.template_datetime)

    @staticmethod
    def __print_message(code: str, old_filename: str, new_filename: str = ''):
        """
        Выводит в консоль отформатированное сообщение.
        """
        click.echo(code.format(old_filename, new_filename))
