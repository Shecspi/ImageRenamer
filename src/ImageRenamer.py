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
    __path: str
    __root_path: str
    __recursion: bool = False
    __is_unique_name: bool = False
    __suffix_for_unique_name: str = ' (copy)'
    __template_datetime_for_new_file: str = '%Y%m%d_%H%M%S'

    message_code: dict = {
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
                                  click.style(' невозможно переименовать. У файла нет EXIF-данных.', fg='yellow')),
        'INCORRECT_EXIF': (click.style('- ', fg='yellow') +
                           click.style('{0}', bold=True, fg='yellow') +
                           click.style(' невозможно переименовать. Не получилось прочитать EXIF-данные.', fg='yellow')),
    }

    __dir_not_exist = (click.style('Директория ', fg='red') +
                       click.style('{0}', bold=True, fg='red') +
                       click.style(' не существует.', fg='red'))

    def __init__(self, path: str):
        self.__path = self.__root_path = str(path)

    def set_path(self, path):
        """ Устанавливает путь директории, в которой происходит переименование файлов. """
        self.__path = path

    def set_template(self, template: str) -> None:
        """Устанавливает шаблон переименования файлов. """
        self.__template_datetime_for_new_file = template

    def set_recursion(self, recursion: False) -> None:
        self.__recursion = recursion

    def set_make_unique_name(self, is_unique_name: bool) -> None:
        self.__is_unique_name = is_unique_name

    def rename(self, preview: bool = False) -> None:
        """
        :param preview: Если True, то будет выведен виртуальный результат переименования, но без переименования.
        :return: None
        """
        try:
            for old_filename in sorted(os.listdir(self.__path)):
                abs_dirname = os.path.abspath(self.__path)  # Например, /home/user/image_folder
                local_dirname = abs_dirname.replace(self.__root_path, '')[1:]  # Например, image_folder/dir1
                full_old_filename = os.path.join(abs_dirname, old_filename)

                if isdir(full_old_filename):
                    # ToDo Добавить флаг
                    if self.__recursion:
                        self.set_path(full_old_filename)
                        self.rename(preview)
                    continue

                # Получаем EXIF-данные из файла и используем их для нового имени.
                # На выходе будет одно из следующих значений:
                #   - корректное новое имя файла
                #   - одна из ошибок из self.message_code если подобратьь имя не удалось
                #   - None, если у файла нет EXIF-данных.
                new_filename = self.__check_availability_to_file(os.path.join(abs_dirname, old_filename))
                local_old_filename = os.path.join(local_dirname, old_filename)

                # Если у файла нет EXIF-данных - печатаем сообщение в консоль и переходим на следующую итерацию цикла.
                if new_filename is None:
                    self.__print_message(self.message_code['FILE_DOESNT_HAVE_EXIF'], local_old_filename)
                    continue

                # В случае возникновения ошибок - печатаем сообщение в консоль и переходим на следующую итерацию цикла.
                if new_filename in self.message_code.values():
                    self.__print_message(new_filename, old_filename)
                    continue

                local_new_filename = os.path.join(local_dirname, new_filename)

                # Если файл с таким именем уже существует в директории, то в зависимости от настроек
                # либо подбираем уникальное имя, либо пишем, что невозможно переименовать, и идём дальше.
                if new_filename in os.listdir(abs_dirname):
                    if self.__is_unique_name:
                        new_filename = self.__make_unique_filename(new_filename, abs_dirname)
                        local_new_filename = os.path.join(local_dirname, new_filename)
                    else:
                        self.__print_message(self.message_code['FILE_EXISTS'],
                                             local_old_filename, local_new_filename)
                        continue

                if not preview:
                    try:
                        os.rename(full_old_filename, os.path.join(abs_dirname, new_filename))
                    except PermissionError:
                        self.__print_message(self.message_code['PERMISSION_DENIED'], local_old_filename)
                        continue
                self.__print_message(self.message_code['SUCCESS'], local_old_filename, local_new_filename)
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
            result = self.message_code['FILE_NOT_EXISTS']
        except PIL.UnidentifiedImageError:
            result = self.message_code['FILE_DOESNT_HAVE_EXIF']
        except KeyError:
            result = self.message_code['FILE_DOESNT_HAVE_EXIF']
        except PermissionError:
            result = self.message_code['PERMISSION_DENIED']
        except ValueError:
            result = self.message_code['INCORRECT_EXIF']

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

        exifdata = image.getexif()[306]
        old_format = self.__try_parsing_date(exifdata)

        return self.__reformat_datetime(old_format) + f'.{extension}'

    @staticmethod
    def __try_parsing_date(datetime_string):
        """
        Проверяет datetime_string на соответствие шиблонам.
        В случае, если совпадение найдено, то возвращает объект типа Datetime.
        Если совпадения не обнаружено возвращает ValueError.
        """
        datetimes_templates = ('%Y:%m:%d %H:%M:%S', '%Y.%m.%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y/%d/%m %H:%M:%S')
        for template in datetimes_templates:
            try:
                return datetime.strptime(datetime_string, template)
            # strptime() возвращает ValueError в случае, если не получилось преобразовать строку в Datetime.
            # Но так как нужно проверить все вариант шаблонов, но просто переходим к следующей итерции цикла.
            # И только если совпадения небыли найдены - возвращает ValueError.
            # Это будет означать, что данные в Datetime некорректные.
            except ValueError:
                continue
        raise ValueError()

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
