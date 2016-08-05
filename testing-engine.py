import os
import subprocess as sub
import sys

def run_test(testcase, *args):
    print('[testing] setup.sh ...')
    ret = sub.call(['sh', 'setup.sh'])
    if ret:
        print('[testing] setup.sh ... error')
        return False

    print('[testing] setup.sh ... done')

    print('[testing] {} ...'.format(testcase))
    ret = sub.call(['sh', testcase] + list(args))
    if ret:
        print('[testing] {} ... error'.format(testcase))
        return False

    print('[testing] {} ... done'.format(testcase))

    print('[testing] teardown.sh ...')
    ret = sub.call(['sh', 'teardown.sh'])
    if ret:
        print('[testing] teardown.sh ... error')
        return False

    print('[testing] teardown.sh ... done')
    return True


def main():
    os.chdir(sys.argv[1])
    testcases = filter(
        lambda x: x.startswith('test') and (x.endswith('.sh') or x.endswith('.cases')),
        sys.argv[2:] if len(sys.argv) > 2 else os.listdir()
    )

    print('[testing] teardown.sh ...')
    ret = sub.call(['sh', 'teardown.sh'])
    if ret != 0:
        print('[testing] teardown.sh ... error')
        return 1

    print('[testing] teardown.sh ... done')

    test_failed = False
    for testcase in testcases:
        if test_failed:
            break

        if testcase.endswith('.cases'):
            with open(testcase) as f:
                for line in f:
                    if test_failed:
                        break

                    if not run_test(*(line.strip().split())):
                        test_failed = True
        else:
            if not run_test(testcase):
                test_failed = True

main()
