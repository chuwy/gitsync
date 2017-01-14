#!/usr/bin/env python

from __future__ import print_function

import contextlib
from datetime import datetime
import json
import os
import subprocess
import sys


def update_config(configs):
    """Expand paths starting with '~' to their absolute paths"""
    for config in configs:
        for setting in configs[config]:
            if setting == 'path':
                configs[config]['path'] = os.path.expanduser(configs[config]['path'])
    return configs


def load_config():
    """Parse repositories' configs from standard configuration file"""
    try:
        config_dir = os.path.join(os.environ['XDG_CONFIG_DIR'], 'gitsync')
    except KeyError:
        home_dir = os.environ['HOME']
        config_dir = os.path.join(home_dir, '.config', 'gitsync')
    config_file = os.path.join(config_dir, 'config.json')
    config_handle = open(config_file, 'r')
    config = json.load(config_handle)
    config_handle.close()
    return update_config(config)


def call(command):
    """Invoke shell command"""
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


@contextlib.contextmanager
def chdir(path):
    """Temporary change directory"""
    curdir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(curdir)


def new_files(path):
    with chdir(path):
        result = call('git status --short')
        for line in result.stdout.readlines():
            if 'A' in line[:2] or 'M' in line[:2]:
                return True
        return False


def unpushed_commits(path):
    with chdir(path):
        return len(call('git cherry').stdout.readlines()) > 0


def commit(conf):
    message = "'Automatic commit via gitsync from %s at %s'" % (COMPUTER, NOW,)
    if conf['add'] == 'ALL':
        call('git add -A')
    else:
        call('git add -u')
    commit_result = call('git commit --message %s' % message)
    for line in commit_result.stdout.readlines():
        print(line, end='')


def push(conf):
    result = call('git push %s --porcelain' % conf['remote'])
    for line in result.stdout.readlines():
        print(line, end='')
    return result


def sync(conf):
    """Index added files, commit and push"""
    with chdir(conf['path']):
        if new_files(conf['path']) or conf['add'] == 'ALL':
            commit(conf)
        else:
            print("No new files")
        if unpushed_commits(conf['path']):
            result = push(conf)
            retval = result.wait()
            if retval != 0:
                print("ERROR!!!")
                if result.stderr:
                    # TODO: notify about error
                    print(result.stderr)
                    sys.exit(retval)
        else:
            print("No unpushed commits")


NOW = str(datetime.now())
COMPUTER = call('uname -n').stdout.readlines()[0].strip()
CONFIG = load_config()


if __name__ == "__main__":
    for k, v in CONFIG.items():
        print('*' * 87)
        print(' ' * 29 + "* SYNCING %s *" % k)
        sync(v)
        print('*' * 87)
