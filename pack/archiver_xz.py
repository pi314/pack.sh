
exts = ('tar.xz', 'xz')

utils = ['xz']


def archive(self, args):
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
        cmd = ['xz', '--stdout']
        print_cmd(['cat', source_file] + ['|'] + cmd + ['>', target_file])

        if not args.dry:
            with open(source_file, 'rb') as sf:
                with open(target_file, 'wb') as tf:
                    p = sub.Popen(cmd, stdin=sf, stdout=tf)
                    p.wait()
                    return (p.returncode == 0)

    elif action == 'tar.xz':
        cmd_tar = ['tar', 'cvf', '-', source_file]
        cmd_z = ['xz', '-']

        print_cmd(cmd_tar + ['|'] + cmd_z + ['>', target_file])

        if not args.dry:
            with open(target_file, 'wb') as tf:
                p1 = sub.Popen(cmd_tar, stdout=sub.PIPE)
                p2 = sub.Popen(cmd_z, stdin=p1.stdout, stdout=tf)
                p1.stdout.close()

                p1.wait()
                p2.wait()

                return (p1.returncode == 0) and (p2.returncode == 0)

    else:
        log_error('[archiver_xz]', 'Unexpected action:', action)
        return False

    return False
