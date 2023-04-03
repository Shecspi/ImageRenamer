import click


class FieldTextString:
    """
    В этом дата-классе реализованы все текстовые строки, которые используются в программе.
    """
    _style_ok = click.style('[  OK  ]  ', fg='green')
    __style_fail = click.style('[ FAIL ]  ', fg='red')

    message_code: dict = {
        'SUCCESS': (_style_ok +
                    click.style('{0} -> ', bold=True, fg='black') +
                    click.style('{1}', bold=True, fg='green')),
        'FILE_EXISTS': (__style_fail +
                        click.style('{0}', bold=True, fg='black') +
                        click.style(' невозможно переименовать, ') +
                        click.style('{1}', bold=True, fg='black') +
                        click.style(' уже существует.')),
        'FILE_NOT_EXISTS': (__style_fail +
                            click.style('{0}', bold=True, fg='black') +
                            click.style(' не существует.')),
        'PERMISSION_DENIED': (__style_fail +
                              click.style('{0}', bold=True, fg='black') +
                              click.style(' невозможно переименовать. Отказано в доступе.')),
        'FILE_DOESNT_HAVE_EXIF': (__style_fail +
                                  click.style('{0}', bold=True, fg='black') +
                                  click.style(' невозможно переименовать. У файла нет EXIF-данных.')),
        'INCORRECT_EXIF': (__style_fail +
                           click.style('{0}', bold=True, fg='black') +
                           click.style(' невозможно переименовать. Не получилось прочитать EXIF-данные.')),
    }

    __dir_not_exist = (__style_fail + click.style('Директория ', fg='white') +
                       click.style('{0}', bold=True, fg='black') +
                       click.style(' не существует.', fg='white'))