
exts = ('tar.gz', 'tgz', 'gz')

utils = ['tar']


def archive(args):
    target_file = args.source_file + '.' + args.fmt

    pipeline = Pipeline(
            ['tar', 'zcvf', target_file, args.source_file],
            dry=args.dry)
    pipeline.print_cmd()

    return pipeline.run()
