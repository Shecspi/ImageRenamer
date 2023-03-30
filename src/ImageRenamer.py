import os
from os.path import isfile
from datetime import datetime

import PIL
from PIL import Image
from pillow_heif import register_heif_opener

import click
import ffmpeg

register_heif_opener()


class FileDoesntHaveExif(Exception):
    ...


class FileObject:
    def __init__(self, root_dir_path: str = '.', is_recursion: bool = False):
        self.__files = list()
        self.__is_recursion = is_recursion
        self.__root_dir_path = root_dir_path

        self.__scan_of_dir(root_dir_path)

    def __len__(self):
        return len(self.__files)

    def __getitem__(self, position):
        return self.__files[position]

    def __setitem__(self, key, value):
        self.__files[key] = value

    def __repr__(self):
        return f'Files of directory {self.__root_dir_path}'

    def __scan_of_dir(self, current_dir: str):
        with os.scandir(current_dir) as files:
            for file in files:
                filename_full = os.path.abspath(os.path.join(current_dir, file))
                filename_short = filename_full.replace(self.__root_dir_path + '/', '')

                if self.__is_recursion and file.is_dir():
                    self.__files.append(self.__scan_of_dir(filename_full))
                if file.is_file():
                    self.__files.append((filename_short, filename_full))
        self.__files = sorted(self.__files)

    def index(self, item: tuple) -> int:
        """
        Возвращает индекс элемента item в списке.
        """
        return self.__files.index(item)

    def append(self, item: tuple) -> None:
        """
        Добавляет новый элемент item в список.
        """
        self.__files.append(item)

    def update(self, old_item: tuple, new_item: tuple) -> None:
        """
        Заменяет old_item на new_item.
        """
        index = self.index(old_item)
        self.__files[index] = new_item


class ImageRenamer:
    """
    Производит переименование всех файлов в текущем каталоге на основе информации из EXIF-данных.
    Директории пропускаются, рекурсивное переименование директорий не поддерживается.
    """
    __root_path: str
    __is_recursion: bool = False
    __is_unique_name: bool = False
    __suffix_for_unique_name: str = ' (copy)'
    __template_datetime_for_new_file: str = '%Y%m%d_%H%M%S'

    __style_ok = click.style('[  OK  ]  ', fg='green')
    __style_fail = click.style('[ FAIL ]  ', fg='red')

    message_code: dict = {
        'SUCCESS': (__style_ok +
                    click.style('{0} -> ', bold=True, fg='black') +
                    click.style('{1}', bold=True, fg='green')),
        'FILE_EXISTS': (__style_fail +
                        click.style('{0}', bold=True, fg='black') +
                        click.style(' невозможно переименовать, ') +
                        click.style('{1}', bold=True, fg='black') +
                        click.style(' уже существует.')),
        'FILE_NOT_EXISTS': (__style_fail +
                            click.style('{0}', bold=True, fg='black') +
                            click.style(' не существует.')),
        'PERMISSION_DENIED': (__style_fail +
                              click.style('{0}', bold=True, fg='black') +
                              click.style(' невозможно переименовать. Отказано в доступе.')),
        'FILE_DOESNT_HAVE_EXIF': (__style_fail +
                                  click.style('{0}', bold=True, fg='black') +
                                  click.style(' невозможно переименовать. У файла нет EXIF-данных.')),
        'INCORRECT_EXIF': (__style_fail +
                           click.style('{0}', bold=True, fg='black') +
                           click.style(' невозможно переименовать. Не получилось прочитать EXIF-данные.')),
    }

    __dir_not_exist = (__style_fail + click.style('Директория ', fg='white') +
                       click.style('{0}', bold=True, fg='black') +
                       click.style(' не существует.', fg='white'))

    def __init__(self, path: str):
        self.__root_path = str(path)

    def set_template(self, template: str) -> None:
        """Устанавливает шаблон переименования файлов. """
        self.__template_datetime_for_new_file = template

    def set_recursion(self, recursion: False) -> None:
        self.__is_recursion = recursion

    def set_make_unique_name(self, is_unique_name: bool) -> None:
        self.__is_unique_name = is_unique_name

    def rename(self, preview: bool = False) -> None:
        """
        :param preview: Если True, то будет выведен виртуальный результат переименования, но без переименования.
        :return: None
        """
        try:
            # Соглашение по именованию переменных
            # *_full - абсолютный адрес файла, например /home/user/folder/a.jpg
            # *_local - локальный адрес файла относительно корневой директории, например folder/a.jpg
            # *_short - имя файла, например a.jpg
            file_objects = FileObject(self.__root_path, self.__is_recursion)
            for old_filename_short, old_filename_full in file_objects:
                old_filename_local = self.__get_local_name_from_full(old_filename_full)
                try:
                    new_filename_full = self.__get_new_filename(old_filename_full)
                    new_filename_short = self.__get_short_name_from_full(new_filename_full)
                except FileNotFoundError:
                    self.__print_message(self.message_code['FILE_NOT_EXISTS'], old_filename_local)
                    continue
                except FileDoesntHaveExif:
                    self.__print_message(self.message_code['FILE_DOESNT_HAVE_EXIF'], old_filename_local)
                    continue
                except KeyError:
                    self.__print_message(self.message_code['FILE_DOESNT_HAVE_EXIF'], old_filename_local)
                    continue
                except PermissionError:
                    self.__print_message(self.message_code['PERMISSION_DENIED'], old_filename_local)
                    continue
                except ValueError:
                    self.__print_message(self.message_code['INCORRECT_EXIF'], old_filename_local)
                    continue

                # Если у файла нет EXIF-данных - печатаем сообщение в консоль и переходим на следующую итерацию цикла.
                if new_filename_short is None:
                    self.__print_message(self.message_code['FILE_DOESNT_HAVE_EXIF'], old_filename_local)
                    continue

                # Если файл с таким именем уже существует в директории, то в зависимости от настроек
                # либо подбираем уникальное имя, либо пишем, что невозможно переименовать, и идём дальше.
                if (new_filename_short, new_filename_full) in file_objects:
                    if self.__is_unique_name:
                        new_filename_full = self.__make_unique_filename(new_filename_full)
                    else:
                        self.__print_message(self.message_code['FILE_EXISTS'],
                                             self.__get_local_name_from_full(old_filename_full),
                                             self.__get_local_name_from_full(new_filename_full))
                        continue

                if not preview:
                    try:
                        os.rename(old_filename_full, new_filename_full)
                    except PermissionError:
                        self.__print_message(self.message_code['PERMISSION_DENIED'], old_filename_full)
                        continue

                file_objects.update(
                    (old_filename_short, old_filename_full),
                    (new_filename_short, new_filename_full)
                )
                self.__print_message(self.message_code['SUCCESS'],
                                     self.__get_local_name_from_full(old_filename_short),
                                     self.__get_local_name_from_full(new_filename_full))
        except FileNotFoundError:
            self.__print_message(self.__dir_not_exist, self.__root_path)

    def __get_new_filename(self, filename) -> str | None:
        """
        Возвращает новое имя для файла 'filename' на основе его EXIF-данных.
        Если файл не содержит EXIF-данных, то возвращает None.
        """
        abs_dirpath = os.sep.join(filename.split(os.sep)[:-1])
        new_filename = os.path.join(abs_dirpath, self.__get_datetime_from_exif(filename))

        return new_filename

    def __get_datetime_from_exif(self, filename: str) -> str | None:
        """
        Пытается получить EXIF-данные из файла, указанного в 'filename'.
        Это может быть изображение, тогда используется модуль PIL,
        или видео, тогда используется модуль ffmpeg.

        В случае успеха - возвращает форматированную строку, пригодную для нового имени файла.
        Если EXIF-информации у файла нет, возвращает None.

        Исключения:
         - FileNotFoundError     файл не существует
         - PermissionError       нет прав доступа к файлу
         - FileDoesntHaveExif   'filename' не является изображением
         - KeyError              нет ключа 306 в EXIF-данных
        """
        try:
            image = Image.open(filename)

            exifdata = image.getexif()[306]
        except PIL.UnidentifiedImageError:
            try:
                exifdata = ffmpeg.probe(filename)['streams'][0]['tags']['creation_time']
            except (KeyError, ffmpeg._run.Error):
                raise FileDoesntHaveExif

        old_format = self.__try_parsing_date(exifdata)
        extension = os.path.splitext(filename)[1]
        return self.__reformat_datetime(old_format) + f'{extension}'

    @staticmethod
    def __try_parsing_date(datetime_string):
        """
        Проверяет 'datetime_string' на соответствие шаблонам.
        В случае, если совпадение найдено, то возвращает объект типа Datetime.

        Исключения:
         - ValueError   не получилось распознать дату и время в EXIF
        """
        datetimes_templates = ('%Y:%m:%d %H:%M:%S', '%Y.%m.%d %H:%M:%S', '%Y/%m/%d %H:%M:%S',
                               '%Y/%d/%m %H:%M:%S', '%Y-%m-%dT%H:%M:%S.000000Z')
        for template in datetimes_templates:
            # strptime() возвращает ValueError в случае, если не получилось преобразовать строку в Datetime.
            # Но так как нужно проверить все вариант шаблонов, но просто переходим к следующей итерции цикла.
            # И только если совпадения небыли найдены - возвращает ValueError.
            # Это будет означать, что данные в Datetime некорректные.
            try:
                return datetime.strptime(datetime_string, template)
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

    def __make_unique_filename(self, filename: str) -> str:
        """
        Добавляет к названию файла 'filename' перед расширением ' (copy)' и возвращает полученное имя.
        :param filename: Имя файла, для которого нужно найти уникальное имя
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
        if isfile(new_filename):
            new_filename = self.__make_unique_filename(new_filename)

        return new_filename

    def __get_local_name_from_full(self, filename_full: str) -> str:
        """
        Возвращает локальное имя файла из полного.
        Например, если __root_path = '/home/user/images', то метод вернёт:
        * filename.jpg
        * folder/filename.jpg
        * folder/folder/filename.jpg
        """
        return filename_full.replace(self.__root_path, '', 1)

    @staticmethod
    def __get_short_name_from_full(filename_full: str) -> str:
        """
        Возвращает имя файла на основе его абсолютного адреса.
        """
        return filename_full.split(os.sep)[-1]
