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
    __path: str = '.'
    __is_make_unique_name: bool = False
    __suffix_for_unique_name: str = ' (copy)'
    __template_datetime_for_new_file: str = '%Y.%m.%d %H:%M:%S'

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

    def set_make_unique_name(self, make_unique_name: bool) -> None:
        self.__is_make_unique_name = make_unique_name

    def rename(self, preview: bool = False) -> None:
        """
        :param preview: Если True, то будет выведен виртуальный результат переименования, но без переименования.
        :return: None
        """
        # Список, в который будут заноситься новые имена файлов в --preview режиме.
        # Он нужен для того, чтобы исключить появление дубликатов.
        list_of_new_filenames: list = []

        try:
            for old_filename in sorted(os.listdir(self.__path)):
                dirname = os.path.abspath(self.__path)
                full_old_filename = os.path.abspath(os.path.join(self.__path, old_filename))

                # Пропускаем все директории.
                # ToDo реализовать возоможность рекурсивного прохождения директорий
                if isdir(os.path.join(dirname, old_filename)):
                    continue

                # Получаем EXIF-данные из файла. В случае возникновения ошибок -
                # печатаем сообщение в консоль и переходим на следующую итерацию цикла.
                new_filename = self.__check_availability_to_file(os.path.join(dirname, old_filename))

                if new_filename in self.result_code.values():
                    self.__print_message(new_filename, old_filename)
                    continue

                if new_filename is not None:
                    if new_filename in os.listdir(dirname):
                        if self.__is_make_unique_name:
                            new_filename = self.__make_unique_filename(new_filename, dirname)
                            if not preview:
                                try:
                                    os.rename(full_old_filename, os.path.join(dirname, new_filename))
                                except PermissionError:
                                    self.__print_message(self.result_code['PERMISSION_DENIED'], old_filename)
                            self.__print_message(self.result_code['SUCCESS'], old_filename, new_filename)
                            continue
                        else:
                            self.__print_message(self.result_code['FILE_EXISTS'], old_filename, new_filename)
                            continue
                    else:
                        if not preview:
                            try:
                                os.rename(full_old_filename, os.path.join(dirname, new_filename))
                            except PermissionError:
                                self.__print_message(self.result_code['PERMISSION_DENIED'], old_filename)
                        self.__print_message(self.result_code['SUCCESS'], old_filename, new_filename)
                        continue
                else:
                    self.__print_message(self.result_code['FILE_DOESNT_HAVE_EXIF'], old_filename)
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
        except KeyError:
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
        old_format = self.__try_parsing_date(exifdata[306])

        return self.__reformat_datetime(old_format) + f'.{extension}'

    def __try_parsing_date(self, datetime_string):
        """ Пытается преобразовать дату 'datetime_string' в тип 'datetime'. """
        datetimes_templates = ('%Y:%m:%d %H:%M:%S', '%Y.%m.%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y/%d/%m %H:%M:%S')
        for template in datetimes_templates:
            try:
                return datetime.strptime(datetime_string, template)
            except:
                pass
        raise ValueError('Datetime format is not valid.')

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

    def __make_unique_filename(self, filename: str, dirname: str) -> str:
        """
        Добавляет к названию файла 'filename' перед расширением ' (copy)' и возвращает полученное имя.
        :param filename: Имя файла, для которого нужно найти уникальное имя
        :param dirname: Абсолютный путь к папке, в которой хранится файл
        :return: Новое имя файла, уникальное для папки dirname
        """
        splited = filename.split('.')
        extention = splited[-1]
        new_filename = ''
        for item in range(0, len(splited) - 1):
            if item == 0:
                new_filename += f'{splited[item]}'
            else:
                new_filename += f'.{splited[item]}'
        new_filename += f'{self.__suffix_for_unique_name}.{extention}'
        if isfile(os.path.join(dirname, new_filename)):
            new_filename = self.__make_unique_filename(new_filename, dirname)

        return new_filename
