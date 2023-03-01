#!/usr/bin/env python3
import click
from src import ImageRenamer


@click.command()
@click.option('-p', '--preview',
              is_flag=True,
              default=False,
              show_default=True,
              help='Отобразить результат работы программы без переименования файлов')
def main(preview: bool):
    renamer = ImageRenamer.ImageRenamer()

    if preview:
        renamer.rename(preview=True)
    else:
        renamer.rename()


if __name__ == '__main__':
    main()
