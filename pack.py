#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess as sub
import sys

from abc import ABCMeta, abstractmethod
from os.path import isfile, isdir, exists, splitext
from shutil import which
from types import SimpleNamespace


if sys.version_info.major < 3:
    print('Need Python3')
    exit(1)


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


dry = False
def print_cmd(cmd):
    print_stderr(
            ('[dry] ' if dry else '') + '$',
            ' '.join(map(
                lambda x: '\033[1;30m' + x + '\033[m' if x in ('|', '>') else shlex.quote(x),
                cmd))
            )


_err_msgs = []
def error(*msg):
    _err_msgs.append(*msg)


def flush_errors():
    if _err_msgs:
        for e in _err_msgs:
            log_error(e)

        exit(1)


def abstract_property(p):
    return property(abstractmethod(p))


class BaseArchiver(metaclass=ABCMeta):
    @abstract_property
    def exts(cls):
        ...

    @abstract_property
    def utils(cls):
        ...

    @property
    def lacked_utils(self):
        return list(filter(lambda x: which(x) is None, self.utils))

    @property
    def why(self):
        if self.lacked_utils:
            return '(need ' + ', '.join(self.lacked_utils) + ')'

        return ''

    def archive(self, args):
        raise NotImplementedError(type(self).__name__ + '.archive()')


class ArchiverTar(BaseArchiver):
    exts = ['tar']
    utils = ['tar']

    def archive(self, args):
        target_file = args.source_file + '.tar'

        cmd = ['tar', 'cvf', target_file, args.source_file]
        print_cmd(cmd)

        if not args.dry:
            p = sub.run(cmd)
            return p.returncode == 0


class ArchiverBz2(BaseArchiver):
    exts = ('tar.bz', 'tbz', 'tar.bz2', 'tbz2', 'bz', 'bz2')
    utils = ['tar']

    @classmethod
    def archive(self, args):
        target_file = args.source_file + '.' + args.fmt

        cmd = ['tar', 'jcvf', target_file, args.source_file]
        print_cmd(cmd)

        if not args.dry:
            p = sub.run(cmd)
            return (p.returncode == 0)


class ArchiverGzip(BaseArchiver):
    exts = ('tar.gz', 'tgz', 'gz')
    utils = ['tar']

    @classmethod
    def archive(self, args):
        target_file = args.source_file + '.' + args.fmt

        cmd = ['tar', 'zcvf', target_file, args.source_file]
        print_cmd(cmd)

        if not args.dry:
            p = sub.run(cmd)
            return (p.returncode == 0)


class ArchiverZ(BaseArchiver):
    exts = ('tar.Z', 'Z')
    utils = ['compress']

    @classmethod
    def archive(self, args):
        source_file = args.source_file
        target_file = None
        action = None

        if args.fmt == 'Z':
            if isdir(args.source_file):
                log_error('[ArchiverZ]', 'Format Z does not support directory')
                return False

            target_file = source_file + '.' + args.fmt
            action = 'Z'

        elif args.fmt == 'tar.Z':
            action = 'Z' if source_file.endswith('.tar') else 'tar.Z'
            target_file = source_file + '.' + action

        else:
            log_error('[ArchiverZ]', 'Unexpected fmt:', args.fmt)
            return False

        if exists(target_file):
            log_error('[ArchiverZ]', 'File already exists:', '[' + magenta(target_file) + ']')
            return False

        if action == 'Z':
            cmd = ['compress', '-c', '-']
            print_cmd(['cat', source_file] + ['|'] + cmd + ['>', target_file])

            if not args.dry:
                with open(source_file, 'rb') as sf:
                    with open(target_file, 'wb') as tf:
                        p = sub.Popen(cmd, stdin=sf, stdout=tf)
                        p.communicate()
                        return (p.returncode == 0)

        elif action == 'tar.Z':
            cmd_tar = ['tar', 'cvf', '-', source_file]
            cmd_z = ['compress', '-c', '-']

            print_cmd(cmd_tar + ['|'] + cmd_z + ['>', target_file])

            if not args.dry:
                with open(target_file, 'wb') as tf:
                    p1 = sub.Popen(cmd_tar, stdout=sub.PIPE)
                    p2 = sub.Popen(cmd_z, stdin=p1.stdout, stdout=tf)
                    p1.stdout.close()

                    p1.wait()
                    p2.wait()

                    return (p1.returncode == 0) and (p2.returncode == 0)

        else:
            log_error('[ArchiverZ]', 'Unexpected action:', action)
            return False

        return False



# Initiate archiver classes
archiver_list = list(map(lambda x: x(), [
        ArchiverTar,
        ArchiverBz2,
        ArchiverGzip,
        ArchiverZ,
        ]))



def usage():
    print_stderr('Usage:')
    print_stderr('  pack [-h|--help]')
    print_stderr('  pack [-v|--verbose] [-n|--dry] [-d|--delete] [-f|--fmt|--format {fmt}] {source_file/dir}')
    print_stderr()
    print_stderr('Optional arguments:')
    print_stderr('  -h, --help      Show this help message and exit.')
    print_stderr('  -v, --verbose   Verbose.')
    print_stderr('  -n, --dry       Print the underlying command and exit.')
    print_stderr('  -d, --delete    Remove source file/dir after packed.')
    print_stderr('  -f {fmt}        Specify the archive format. Default: tar')
    print_stderr()
    print_stderr('Supported formats:')

    for x in archiver_list:
        print_stderr('  ' + ' / '.join(x.exts) + ('' if not x.lacked_utils else ' (not available: need ' + ', '.join(x.lacked_utils) + ')'))

    print_stderr()
    print_stderr('Example:')
    print_stderr('  $ pack -d -f tar my_dir')
    exit(1)


def parse_args(args):
    ret = SimpleNamespace()

    # Initialize variables
    verbose = False
    dry = False
    del_source_file = False
    fmt = 'tar'
    source_file = ''

    # Parse arguments
    try:
        while len(args):
            arg = args.pop(0)

            if arg in ('-h', '--help'):
                usage()

            elif arg in ('-v', '--verbose'):
                if verbose:
                    error('Too verbose')

                verbose = True

            elif arg in ('-n', '--dry'):
                if dry:
                    error('Too dry')

                dry = True

            elif arg in ('-d', '--delete'):
                del_source_file = True

            elif arg in ('-f', '--fmt', '--format'):
                fmt = args.pop(0)

            elif arg.startswith('-'):
                error('Unknown argument: [' + red(arg) + ']')

            elif not source_file:
                source_file = arg

            else:
                error('Too much source file/directory: [' + red(arg) + ']')

    except IndexError:
        error('Argument error')
        flush_errors()

    ret.verbose = verbose
    ret.dry = dry
    ret.del_source_file = del_source_file
    ret.fmt = fmt.lstrip('.')
    ret.source_file = source_file

    return ret


def main():
    args = parse_args(sys.argv[1:])

    def why(x):
        if x.lacked_utils:
            return '(need ' + ', '.join(x.lacked_utils) + ')'

        return ''

    if args.verbose:
        log('[args]', 'verbose', '=', args.verbose)
        log('[args]', 'dry', '=', args.dry)
        log('[args]', 'del_source_file', '=', args.del_source_file)
        log('[args]', 'fmt', '=', '[' + magenta(args.fmt) + ']')
        log('[args]', 'source_file', '=', '[' + magenta(args.source_file) + ']')
        for x in archiver_list:
            log('[status]', type(x).__name__ + '.available =', not x.lacked_utils, why(x))

    global dry
    dry = args.dry

    # Call corresponding archiver to handle
    archiver = (list(filter(
        lambda x: (args.fmt in x.exts),
        archiver_list
        )) + [None])[0]

    if not archiver or archiver.lacked_utils:
        error('Unsupported format: [{fmt}]{why}'.format(
            fmt=red(args.fmt),
            why='' if not archiver or not archiver.lacked_utils else ' ' + why(archiver),
            ))

    # Argument sanity check
    if not args.source_file:
        error('Need to provide source file/directory')

    elif not exists(args.source_file):
        error('Source file [' + red(args.source_file) + '] does not exist')

    elif not isfile(args.source_file) and not isdir(args.source_file):
        error('Source file is neither a file nor a dir')

    elif archiver is not None and args.source_file.endswith(tuple(map(lambda x: '.' + x, archiver.exts))):
        error('Nothing to do')

    flush_errors()

    res = archiver.archive(args)
    if not res:
        log_error('res', '=', res)

    elif args.verbose:
        log('res', '=', res)

    if args.del_source_file:
        cmd = ['rm'] + (['-r'] if isdir(args.source_file) else []) + [args.source_file]

        if args.dry or res == True:
            print_cmd(cmd)

        if res == True:
            sub.run(cmd)


if __name__ == '__main__':
    main()
