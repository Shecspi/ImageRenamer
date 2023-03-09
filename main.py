#!/usr/bin/env python3
import click
from src import ImageRenamer


@click.command()
@click.argument('path', default='.', type=str)
@click.option('-p', '--preview',
              is_flag=True,
              default=False,
              show_default=True,
              help='Отобразить результат работы программы без переименования файлов.')
@click.option('-t', '--template',
              default='%Y%m%d_%H%M%S',
              show_default=True,
              help='Шаблон, на основе которого будет производиться переименование файлов.')
@click.option('-u', '--make-unique-name',
              is_flag=True,
              default=True,
              show_default=True,
              help='При совпадении имён файла добавлять суффикс в конец имени. ' +
                   'Если False, то файл с таким же именем будет перезаписан.')
@click.option('-r', '--recursion',
              is_flag=True,
              default=False,
              show_default=True,
              help='Если флаг установлен, то программа будет рекурсивно ' +
                   'проходить каталоги и переименовывать в них файлы.')
def main(path: str = '',
         preview: bool = False,
         template: str = '%Y.%m.%d %H:%M:%S',
         make_unique_name: bool = False,
         recursion: bool = False) -> None:
    renamer = ImageRenamer.ImageRenamer(path)
    renamer.set_template(template)
    renamer.set_make_unique_name(make_unique_name)
    renamer.set_recursion(recursion)
    if preview:
        renamer.rename(preview=True)
    else:
        renamer.rename()


if __name__ == '__main__':
    main()
