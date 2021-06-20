
exts = ['tar']

utils = ['tar']


def archive(self, args):
    target_file = args.source_file + '.tar'

    cmd = ['tar', 'cvf', target_file, args.source_file]
    print_cmd(cmd)

    if not args.dry:
        p = sub.run(cmd)
        return p.returncode == 0
