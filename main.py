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
              default='%Y.%m.%d %H:%M:%S',
              show_default=True,
              help='Шаблон, на основе которого будет производиться переименование файлов.')
@click.option('--make-unique-name',
              is_flag=True,
              default=False,
              show_default=True,
              help='При совпадении имён файла добавлять порядковый номер в конец имени.')
def main(path: str, preview: bool, template: str, make_unique_name: bool = False) -> None:
    renamer = ImageRenamer.ImageRenamer()
    renamer.set_path(path)
    renamer.set_template(template)
    renamer.set_make_unique_name(make_unique_name)
    if preview:
        renamer.rename(preview=True)
    else:
        renamer.rename()


if __name__ == '__main__':
    main()
