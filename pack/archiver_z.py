from os.path import isdir, exists

from .utils import Pipeline, FileRedirect


exts = ('tar.Z', 'Z')

utils = ['compress']


def archive(args):
    source_file = args.source_file
    target_file = None
    action = None

    if args.fmt == 'Z':
        if isdir(args.source_file):
            log_error('[archiver_z]', 'Format Z does not support directory')
            return False

        target_file = source_file + '.' + args.fmt
        action = 'Z'

    elif args.fmt == 'tar.Z':
        action = 'Z' if source_file.endswith('.tar') else 'tar.Z'
        target_file = source_file + '.' + action

    else:
        log_error('[archiver_z]', 'Unexpected fmt:', args.fmt)
        return False

    if exists(target_file):
        log_error('[archiver_z]', 'File already exists:', '[' + magenta(target_file) + ']')
        return False

    if action == 'Z':
        pipeline = Pipeline(
                FileRedirect(source_file),
                ['compress', '-c', '-'],
                FileRedirect(target_file),
                dry=args.dry)
        pipeline.print_cmd()

        return pipeline.run()

    elif action == 'tar.Z':
        pipeline = Pipeline(
                ['tar', 'cvf', '-', source_file],
                ['compress', '-c', '-'],
                FileRedirect(target_file),
                dry=args.dry)
        pipeline.print_cmd()

        return pipeline.run()

    else:
        log_error('[archiver_z]', 'Unexpected action:', action)
        return False

    return False
