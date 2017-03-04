#!/usr/bin/env python3

from sys import argv, stderr
from os import geteuid, listdir
from os.path import exists
import subprocess

def error(message):
    print('\033[31m' + message + '\033[0m', file=stderr)
    exit(1)


def default(opt, var):
    args = {
            '--dest' : '/.snapshots',
            '--volume' : [],
            '--limits' : 3
            }
    if args[opt] == var:
        return True
    return False


def merge(A, B):
    result = dict(A)
    
    for e in B:
        if e == '--volume':
            result[e] += B[e]
        elif default(e, A[e]) == True:
            result[e] = B[e]

    return result


def read_conf(path):
    args = {
            '--dest' : '/.snapshots',
            '--volume' : [],
            '--limits' : 3
            }

    conf = open(path)
    
    for line in conf:
        arg = line.split()
        if len(arg) == 0:
            continue
        if arg[0] not in args:
            error('unknown args')
        elif arg[0] == '--dest':
            args['--dest'] = arg[1]
        elif arg[0] == '--limits':
            args['--limits'] = arg[1]
        elif arg[0] == '--volume':
            for i in range(1, len(arg)):
                args['--volume'].append(arg[i])

    conf.close()
    
    return args
 

def print_help():
    print(
            """%s
            --help      print help
            --dest      destination directory for snapshots
            --volume    list of subolumins to create snapshot  
            --conf      read config file [default /etc/pjbackup/conf]
            --limits    number of snapshots
            """%(argv[0]), file=stderr)


def move(old, new):
    if exists(new):
        subprocess.run(['/bin/btrfs', 'subvolume', 'delete', new])
    subprocess.run(['/bin/btrfs', 'subvolume', 'snapshot', old, new])
    subprocess.run(['/bin/btrfs', 'subvolume', 'delete', old])


def create_snapshot(volume, snap):
    if exists(snap):
        subprocess.run(['/bin/btrfs', 'subvolume', 'delete', snap])
    subprocess.run(['/bin/btrfs', 'subvolume', 'snapshot', volume, snap])


def parse(path):
    path = str(path)
    idx = len(path) - 1
    while idx > 0 and path[idx] != '/':
        idx -= 1
    return path[idx + 1:]

def parse_argv():
    args = {
            '--dest' : '/.snapshots',
            '--volume' : [],
            '--conf' : '/etc/pjbackup/conf',
            '--limits' : 3
            }
    last = None
    for i in range(1, len(argv)):
        if argv[i] in args:
            last = argv[i]
            if last == '--help':
                print_help()
                exit(0)
        else:
            if last == None:
                error('wrong args')
            if last == '--dest':
                args[last] = argv[i]
                last = None
            elif last == '--volume':
                args[last].append(argv[i])
            elif last == '--conf':
                args[last] = argv[i]
            else:
                error('unknown args')

    return args


def move_old_snapshots(dest, limit):
    dirs = sorted(listdir(dest))
    dirs.reverse()
    for snap in dirs:
        if int(snap[-1]) >= int(limit):
            continue
        new_snap = snap[:-1] + str(int(snap[-1]) + 1)
        move(dest + '/' + snap, dest + '/' + new_snap)


def main():
    if geteuid() != 0:
        error('error: pjbackup requires superuser privilege')

    args = parse_argv()
    args = merge(args, read_conf(args['--conf']))

    move_old_snapshots(args['--dest'], args['--limits'])
    
    for snap in args['--volume']:
        create_snapshot(snap, args['--dest'] + '/' + parse(snap) + '_1')

    exit(0)


if __name__=='__main__':
    main()
