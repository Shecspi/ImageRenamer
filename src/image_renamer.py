import os
from os.path import isfile
from datetime import datetime
from exif import Image


class Rename:
    # Формат даты и времени, по которому извлекается информация из EXIF.
    # В моих фотографиях он именно такой, но не исключаю, что в других фотоаппаратах может отличаться.
    standart_format_of_datetime: str = '%Y:%m-%d %H:%M:%S'

    # Шаблон для нового имени файла
    template_datetime: str = '%Y-%m-%d %H-%M-%S'

    def __init__(self):
        for filename in sorted(os.listdir()):
            if isfile(filename):
                try:
                    new_name = self._get_datetime_from_exif(filename)
                except ValueError:
                    print(f'- "{filename}" содержит некорректный формат EXIF-даты.')
                    continue

                if new_name:
                    try:
                        self._rename_file(filename, new_name)
                        print(f'+ "{filename}" успешно переименован в "{new_name}"')
                    except FileExistsError:
                        print(f'- "{new_name}" уже существует. "{filename}" не переименован.')
                else:
                    print(f'- "{filename}" не содержит EXIF-информации')

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
