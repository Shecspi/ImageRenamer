import os
from os.path import isfile, isdir
from datetime import datetime

import PIL
from PIL import Image
from pillow_heif import register_heif_opener

import click

register_heif_opener()


class ImageRenamer:
    """
    Производит переименование всех файлов в текущем каталоге на основе информации из EXIF-данных.
    Директории пропускаются, рекурсивное переименование директорий не поддерживается.
    """
    # Формат даты и времени, по которому извлекается информация из EXIF.
    # В моих фотографиях он именно такой, но не исключаю, что в других фотоаппаратах может отличаться.
    __standart_format_of_datetime: str = '%Y:%m:%d %H:%M:%S'

    # Шаблон для нового имени файла
    __template_datetime_for_new_file: str

    __path: str

    result_code: dict = {
        'SUCCESS': (click.style('+ ', fg='green') +
                    click.style('{0}', bold=True, fg='green') +
                    click.style(' -> ', fg='green') +
                    click.style('{1}', bold=True, fg='green')),
        'FILE_EXISTS': (click.style('- ', fg='red') +
                        click.style('{0}', bold=True, fg='red') +
                        click.style(' невозможно переименовать, ', fg='red') +
                        click.style('{1}', bold=True, fg='red') +
                        click.style(' уже существует.', fg='red')),
        'FILE_NOT_EXISTS': (click.style('- ', fg='red') +
                            click.style('{0}', bold=True, fg='red') +
                            click.style(' не существует.', fg='red')),
        'PERMISSION_DENIED': (click.style('- ', fg='red') +
                              click.style('{0}', bold=True, fg='red') +
                              click.style(' невозможно переименовать. Отказано в доступе.', fg='red')),
        'FILE_DOESNT_HAVE_EXIF': (click.style('- ', fg='yellow') +
                                  click.style('{0}', bold=True, fg='yellow') +
                                  click.style(' невозможно переименовать. У файла нет EXIF-данных.', fg='yellow'))
    }

    __dir_not_exist = (click.style('Директория ', fg='red') +
                       click.style('{0}', bold=True, fg='red') +
                       click.style(' не существует.', fg='red'))

    def set_path(self, path):
        """ Устанавливает путь директории, в которой происходит переименование файлов. """
        self.__path = path

    def set_template(self, template: str) -> None:
        """Устанавливает шаблон переименования файлов. """
        self.__template_datetime_for_new_file = template

    def rename(self, preview: bool = False) -> None:
        """
        :param preview: Если True, то будет выведен виртуальный результат переименования, но без переименования.
        :return: None
        """
        # Список, в который будут заноситься новые имена файлов в --preview режиме.
        # Он нужен для того, чтобы исключить появление дубликатов.
        list_of_new_filenames: list = []

        try:
            for short_old_filename in sorted(os.listdir(self.__path)):
                full_old_filename = os.path.abspath(os.path.join(self.__path, short_old_filename))

                # Пропускаем все директории.
                # ToDo реализовать возоможность рекурсивного прохождения директорий
                if isdir(full_old_filename):
                    continue

                # Получаем EXIF-данные из файла. В случае возникновения ошибок -
                # печатаем сообщение в консоль и переходим на следующую итерацию цикла.
                short_new_filename = self.__check_availability_to_file(full_old_filename)
                full_new_filename = os.path.abspath(os.path.join(self.__path, short_new_filename))

                if short_new_filename in self.result_code.values():
                    self.__print_message(short_new_filename, short_old_filename)
                    continue

                if short_new_filename is not None:
                    # Если файл с таким названием уже существует - выдаём сообщение о невозможности переименования
                    # и переходим на следующую итерацию цикла.
                    if isfile(full_new_filename):
                        self.__print_message(self.result_code['FILE_EXISTS'], short_old_filename, short_new_filename)
                        continue

                    # Если установлен фалг --preview, то производим отображение результата без переименования файлов.
                    # Для исключения создания файлов с одинаковым именем, используется список list_of_new_filenames.
                    # Если в нём уже есть элемент с таким же именем, то выводится соответствующее сообщение.
                    if preview:
                        if short_new_filename in list_of_new_filenames:
                            self.__print_message(self.result_code['FILE_EXISTS'], short_old_filename, short_new_filename)
                            continue
                        self.__print_message(self.result_code['SUCCESS'], short_old_filename, short_new_filename)
                        list_of_new_filenames.append(short_new_filename)
                    # Если флага --preview нет, то переименовываем файлы
                    else:
                        try:
                            os.rename(full_old_filename, full_new_filename)
                            self.__print_message(self.result_code['SUCCESS'], short_old_filename, short_new_filename)
                        except PermissionError:
                            self.__print_message(self.result_code['PERMISSION_DENIED'], short_old_filename)
                else:
                    self.__print_message(self.result_code['FILE_DOESNT_HAVE_EXIF'], short_old_filename)
        except FileNotFoundError:
            self.__print_message(self.__dir_not_exist, self.__path)

    def __check_availability_to_file(self, filename) -> str | None:
        """
        Пытается получить EXIF-данные из файла.
        Если файл не содержит EXIF-данных, то возвращает None.
        В случае успеха возвращает строку str, содержащую новое имя для файла.
        Если произошло исключение, то возвращает строку str с кодом ошибки.
        """
        try:
            result = self.__get_datetime_from_exif(filename)
        except FileNotFoundError:
            result = self.result_code['FILE_NOT_EXISTS']
        except PIL.UnidentifiedImageError:
            result = self.result_code['FILE_DOESNT_HAVE_EXIF']
        except PermissionError:
            result = self.result_code['PERMISSION_DENIED']

        return result

    def __get_datetime_from_exif(self, filename: str) -> str | None:
        """
        Пытается получить EXIF-данные из файла, указанного в 'filename'.
        В случае успеха - возвращает форматированную строку, пригодную для нового имени файла.
        Если EXIF-информации у файла нет, возвращает False.

        В случае, если формат даты и времени в EXIF не соответствует стандартному, вызывается исключение ValueError.
        """
        image = Image.open(filename)
        extension = filename.split('.')[-1]

        exifdata = image.getexif()
        old_format = datetime.strptime(exifdata[306], self.__standart_format_of_datetime)

        return self.__reformat_datetime(old_format) + f'.{extension}'

    def __reformat_datetime(self, old_format: datetime) -> str:
        """
        Возвращает строку с изменённым на основе шаблона форматом даты и времени.
        """
        return datetime.strftime(old_format, self.__template_datetime_for_new_file)

    @staticmethod
    def __print_message(code: str, old_filename: str, new_filename: str = ''):
        """
        Выводит в консоль отформатированное сообщение.
        """
        click.echo(code.format(old_filename, new_filename))
