__all__ = ['dedent', 'indent']


def dedent(text):
    """Remove indentation from text as measured by the first non-empty line."""
    indentedlines = text.rstrip().split('\n')

    while indentedlines[0] == '':
        indentedlines.pop(0)

    firstline = indentedlines[0]

    indent = len(firstline) - len(firstline.lstrip())

    dedentedlines = []
    for indented in indentedlines:
        assert indented == '' or indented[:indent].strip() == '', `indented`
        dedentedlines.append(indented[indent:])

    return '\n'.join(dedentedlines) + '\n'


def indent(text, amount=2):
    """Indent text by amount spaces."""
    indent = ' ' * amount
    separator = '\n' + indent
    return indent + separator.join(text.rstrip().split('\n')) + '\n'
