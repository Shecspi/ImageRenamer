from dataclasses import dataclass


@dataclass
class FieldCounter:
    """
    В этом дата-классе реализованы счётчики переименованных и неперрименованных файлов..
    """
    _renamed_qty: int = 0
    _failed_qty: int = 0
