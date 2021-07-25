import shlex
import subprocess as sub
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
    def __init__(self, fpath):
        self.fpath = fpath


class Pipeline:
    def __init__(self, *cmds, dry=False):
        type_error = False
        if not isinstance(cmds, (list, tuple)):
            type_error = True

        else:
            for idx, cmd in enumerate(cmds):
                if isinstance(cmd, FileRedirect):
                    if idx == 0 or idx == len(cmds) - 1:
                        continue
                    else:
                        type_error = True

                if not isinstance(cmd, (list, tuple)):
                    type_error = True

                else:
                    for arg in cmd:
                        if not isinstance(arg, str):
                            type_error = True

        if type_error:
            raise TypeError('Must provide [FileRedirect|] + List[List[Str]] + [FileRedirect|]')

        self.cmds = cmds
        self.dry = dry

    def print_cmd(self):
        tokens = []

        if self.dry:
            tokens.append('[dry]')

        tokens.append('$')

        for idx, cmd in enumerate(self.cmds):
            if isinstance(cmd, FileRedirect):
                if idx == 0:
                    tokens.append('cat {}'.format(cmd.fpath))

                elif idx == len(self.cmds) - 1:
                    tokens.append(black('>') + ' {}'.format(cmd.fpath))

                else:
                    tokens.append('(error: {})'.format(cmd.fpath))

            else:
                if idx != 0:
                    tokens.append(black('|'))

                tokens.append(' '.join(map(shlex.quote, cmd)))

        print_stderr(' '.join(tokens))

    def run(self):
        if self.dry:
            return False

        cmds = list(self.cmds)
        if isinstance(cmds[0], FileRedirect):
            input_file = open(cmds[0].fpath, 'rb')
            cmds = cmds[1:]
        else:
            input_file = None

        if isinstance(cmds[-1], FileRedirect):
            output_file = open(cmds[-1].fpath, 'wb')
            cmds = cmds[:-1]
        else:
            output_file = None

        plist = []
        for idx, cmd in enumerate(cmds):
            if idx == 0:
                stdin = input_file
            else:
                stdin = plist[-1].stdout

            if idx == len(cmds) - 1:
                stdout = output_file
            else:
                stdout = sub.PIPE

            plist.append(sub.Popen(cmd, stdin=stdin, stdout=stdout))

        for p in plist:
            if p.stdout:
                p.stdout.close()

        for p in plist:
            p.wait()

        if input_file:
            input_file.close()

        if output_file:
            output_file.close()

        for p in plist:
            if p.returncode != 0:
                return False

        return True
