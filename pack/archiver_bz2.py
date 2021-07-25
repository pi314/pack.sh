
exts = ('tar.bz', 'tbz', 'tar.bz2', 'tbz2', 'bz', 'bz2')

utils = ['tar']


def archive(args):
    target_file = args.source_file + '.' + args.fmt

    pipeline = Pipeline(
            ['tar', 'jcvf', target_file, args.source_file],
            dry=args.dry)
    pipeline.print_cmd()

    return pipeline.run()
