import os


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

                if self.__is_recursion and file.is_dir():
                    self.__files.append(self.__scan_of_dir(filename_full))
                if file.is_file():
                    self.__files.append(filename_full)
        self.__files = sorted(self.__files)

    def index(self, item: str) -> int:
        """
        Возвращает индекс элемента item в списке.
        """
        return self.__files.index(item)

    def append(self, item: str) -> None:
        """
        Добавляет новый элемент item в список.
        """
        self.__files.append(item)

    def update(self, old_item: str, new_item: str) -> None:
        """
        Заменяет old_item на new_item.
        """
        index = self.index(old_item)
        self.__files[index] = new_item
