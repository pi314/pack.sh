from os.path import isdir, exists

from .utils import Pipeline, FileRedirect


exts = ('tar.xz', 'xz')

utils = ['xz']


def archive(args):
    source_file = args.source_file
    target_file = None
    action = None

    if args.fmt == 'xz':
        if isdir(args.source_file):
            log_error('[archiver_xz]', 'Format Z does not support directory')
            return False

        target_file = source_file + '.' + args.fmt
        action = 'xz'

    elif args.fmt == 'tar.xz':
        action = 'xz' if source_file.endswith('.tar') else 'tar.xz'
        target_file = source_file + '.' + action

    else:
        log_error('[archiver_xz]', 'Unexpected fmt:', args.fmt)
        return False

    if exists(target_file):
        log_error('[archiver_xz]', 'File already exists:', '[' + magenta(target_file) + ']')
        return False

    if action == 'xz':
        pipeline = Pipeline(
                FileRedirect(source_file),
                ['xz', '--stdout'],
                FileRedirect(target_file),
                dry=args.dry)
        pipeline.print_cmd()

        return pipeline.run()

    elif action == 'tar.xz':
        pipeline = Pipeline(
                ['tar', 'cvf', '-', source_file],
                ['xz', '-'],
                FileRedirect(target_file),
                dry=args.dry)
        pipeline.print_cmd()

        return pipeline.run()

    else:
        log_error('[archiver_xz]', 'Unexpected action:', action)
        return False

    return False
