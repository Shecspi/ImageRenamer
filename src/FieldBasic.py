from dataclasses import dataclass

import click


@dataclass
class FieldBasic:
    """
    В этом дата-классе объявлены все основные поля, которые пользователь может указывает в момент запуска программы.
    """
    root_path: str
    is_recursion: bool = False
    is_unique_name: bool = False
    suffix_for_unique_name: str = ' (copy)'
    template_datetime_for_new_file: str = '%Y%m%d_%H%M%S'

    def __post_init__(self):
        """
        По-умолчанию, _root_path яввляется объектом типа LocalPath.
        Для удобной работы преобразуем его в str.
        """
        self.root_path = str(self.root_path)
