import importlib

from shutil import which


_archiver_name_list = [
        'archiver_tar',
        'archiver_bz2',
        'archiver_gzip',
        'archiver_z',
        'archiver_xz',
        'archiver_zip',
        'archiver_7z',
        ]

_archiver_list = None


def archiver_list():
    global _archiver_list

    if not _archiver_list:
        _archiver_list = [
                importlib.import_module('.' + archiver, package='pack')
                for archiver in _archiver_name_list
                ]

        _archiver_list = [x
                for x in _archiver_list
                if hasattr(x, 'exts') and hasattr(x, 'utils')
                ]

        for n, x in zip(_archiver_name_list, _archiver_list):
            x.name = n
            x.lacked_utils = lacked_utils(x)

    return _archiver_list


def lacked_utils(x):
    return [u for u in x.utils if which(u) is None]
