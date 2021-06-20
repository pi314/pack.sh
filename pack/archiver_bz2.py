
exts = ('tar.bz', 'tbz', 'tar.bz2', 'tbz2', 'bz', 'bz2')

utils = ['tar']


def archive(self, args):
    target_file = args.source_file + '.' + args.fmt

    cmd = ['tar', 'jcvf', target_file, args.source_file]
    print_cmd(cmd)

    if not args.dry:
        p = sub.run(cmd)
        return (p.returncode == 0)
