#!/usr/bin/env python3
import click
from src import ImageRenamer


@click.command()
@click.option('-p', '--preview',
              is_flag=True,
              default=False,
              show_default=True,
              help='Отобразить результат работы программы без переименования файлов.')
@click.option('-t', '--template',
              default='%Y:%m:%d %H:%M:%S',
              show_default=True,
              help='Шаблон, на основе которого будет производиться переименование файлов.')
def main(preview: bool, template: str):
    renamer = ImageRenamer.ImageRenamer()
    renamer.set_template(template)
    if preview:
        renamer.rename(preview=True)
    else:
        renamer.rename()


if __name__ == '__main__':
    main()
