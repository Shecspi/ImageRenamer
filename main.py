import os
from os.path import isfile
from datetime import datetime
from exif import Image


class ImageRenamer:
    def __init__(self):
        for item in sorted(os.listdir()):
            if isfile(item):
                new_name = self._get_datetime_from_exif(item)

                if new_name:
                    self._rename_file(item, new_name)

    def _get_datetime_from_exif(self, filename: str):
        image = Image(filename)

        if image.has_exif:
            old_format = datetime.strptime(image.datetime_original, '%Y:%m:%d %H:%M:%S')

            return self._reformat_datetime(old_format)

        return False

    def _reformat_datetime(self, old_format: datetime) -> str:
        return datetime.strftime(old_format, '%Y-%m-%d %H-%M-%S')

    def _rename_file(self, old_name: str, new_name: str):
        os.rename(old_name, new_name)


if __name__ == '__main__':
    ImageRenamer()
