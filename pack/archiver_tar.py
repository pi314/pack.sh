from .utils import Pipeline, FileRedirect


exts = ['tar']

utils = ['tar']


def archive(args):
    target_file = args.source_file + '.tar'

    pipeline = Pipeline(
            ['tar', 'cvf', target_file, args.source_file],
            dry=args.dry)
    pipeline.print_cmd()

    return pipeline.run()
