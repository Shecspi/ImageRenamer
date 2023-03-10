#!/usr/bin/env python3
import click
import settings
from src import ImageRenamer


@click.command()
@click.argument('path', default='.', type=str)
@click.option('-p', '--preview',
              is_flag=True,
              default=settings.PREVIEW,
              show_default=True,
              help='Отобразить результат работы программы без переименования файлов.')
@click.option('-t', '--template',
              default=settings.TEMPLATE,
              show_default=True,
              help='Шаблон, на основе которого будет производиться переименование файлов.')
@click.option('-u', '--unique-name',
              is_flag=True,
              default=settings.UNIQUE_NAME,
              show_default=True,
              help='При совпадении имён файла добавлять суффикс в конец имени. ' +
                   'Если False, то файл с таким же именем будет перезаписан.')
@click.option('-r', '--recursion',
              is_flag=True,
              default=settings.RECURSION,
              show_default=True,
              help='Если флаг установлен, то программа будет рекурсивно ' +
                   'проходить каталоги и переименовывать в них файлы.')
def main(path: str, preview: bool, recursion: bool,
         template: str, unique_name: bool) -> None:
    print(template)
    renamer = ImageRenamer.ImageRenamer(path)
    renamer.rename(preview)
    renamer.set_recursion(recursion)
    renamer.set_template(template)
    renamer.set_make_unique_name(unique_name)


if __name__ == '__main__':
    main()
