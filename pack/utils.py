import sys


def print_stderr(*args, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def color_str(color):
    def curry(*s):
        return '\033[1;3' + str(color) + 'm' + ' '.join(s) + '\033[m'

    return curry

black = color_str(0)
nocolor = (lambda x: x)
red = color_str(1)
green = color_str(2)
yellow = color_str(3)
blue = color_str(4)
magenta = color_str(5)
cyan = color_str(6)
white = color_str(7)


def log(*args, level='verbose'):
    if level == 'error':
        level = red(level)

    print_stderr('(' + level + ')', *args)


def log_error(*args):
    log(*args, level='error')


class FileRedirect:
    def __init__(self, fname):
        self.fname = fname


class Pipeline:
    def __init__(self, cmds, dry=False):
        type_error = False
        if not isinstance(cmds, (list, tuple)):
            type_error = True

        else:
            for cmd in cmds:
                if not isinstance(cmd, (list, tuple)):
                    type_error = True

                else:
                    for arg in cmd:
                        if not isinstance(arg, str):
                            type_error = True

        if type_error:
            raise TypeError('Must provide List[List[Str]]')

        self.cmds = cmds
