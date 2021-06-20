
exts = ('tar.gz', 'tgz', 'gz')

utils = ['tar']


def archive(self, args):
    target_file = args.source_file + '.' + args.fmt

    cmd = ['tar', 'zcvf', target_file, args.source_file]
    print_cmd(cmd)

    if not args.dry:
        p = sub.run(cmd)
        return (p.returncode == 0)
