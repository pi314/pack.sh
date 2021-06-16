#!/usr/bin/env python3

import importlib
import os
import shlex
import subprocess as sub
import sys

from os.path import isfile, isdir, exists, splitext
from types import SimpleNamespace

from .utils import *


archiver_name_list = [
        'archiver_tar',
        'archiver_bz2',
        'archiver_gzip',
        'archiver_z',
        'archiver_xz',
        ]


# Initiate archiver classes
archiver_list = [
        getattr(importlib.import_module('.' + archiver, package='pack'), archiver)()
        for archiver in archiver_name_list
        ]


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
    log('WIP')
    log(args)

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

    exit(0)

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
