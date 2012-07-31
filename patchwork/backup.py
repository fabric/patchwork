"""
Module providing easy API for very basic backup/rollback functionality of files.
"""

from __future__ import with_statement

from fabric.api import sudo, run, settings, hide 

def backup_file(file_path, use_sudo=False, verbose=False):
    """
    Create a backup of ``file_path`` by creating a copy in the original
    directory, suffixed with a dash(-) and a date expression "%d%m%y_%H%M%S". 
    For example:
    /path/to/origfile.conf becomes /path/to/origfile.conf-310712_142231

    If ``use_sudo`` is True, will use `sudo` instead of `run`.

    `backup_file` will, by default, hide all output (including the run line, stdout,
    stderr and any warning resulting from the file not existing) in order to
    avoid cluttering output. You may specify ``verbose=True`` to change this
    behavior.
    """
    func = use_sudo and sudo or run

    cmd = 'cp %s %s-`date +\"%%d%%m%%y_%%H%%M%%S\"`' % (file_path, file_path)

    if verbose:
        with settings(warn_only=True):
            return func(cmd).succeeded

    with settings(hide('everything'), warn_only=True):
        return func(cmd).succeeded


def find_latest_backup(file_path, use_sudo=False, verbose=False): 
    """
    Find latest file created with `backup_file` for ``file_path``.
    `find_latest_backup` looks for the latest file in the directory of 
    the given ``file_path`` suffixed with the pattern '-[0-9]*_[0-9]*'

    If ``use_sudo`` is True, will use `sudo` instead of `run`.

    `find_latest_backup` will, by default, hide all output (including the run line, stdout,
    stderr and any warning resulting from the file not existing) in order to
    avoid cluttering output. You may specify ``verbose=True`` to change this
    behavior.
    """
    func = use_sudo and sudo or run

    cmd = 'ls -t %s-[0-9]*_[0-9]* | head -1' % file_path

    if verbose:
        with settings(warn_only=True):
            return func(cmd)

    with settings(hide('everything'), warn_only=True):
        return func(cmd)


def rollback_latest_backup(file_path, use_sudo=False, verbose=False):
    """
    Overwrite ``file_path`` with its latest backup as found with `find_latest_backup`.
    The original ``file_path`` will be erased without backup.

    If ``use_sudo`` is True, will use `sudo` instead of `run`.

    `rollback_latest_backup` will, by default, hide all output (including the run line, stdout,
    stderr and any warning resulting from the file not existing) in order to
    avoid cluttering output. You may specify ``verbose=True`` to change this
    behavior.
    """
    func = use_sudo and sudo or run

    latest_backup = find_latest_backup(file_path)

    cmd = 'cp %s %s' % (latest_backup, file_path)

    if verbose:
       with settings(warn_only=True):
           return func(cmd).succeeded

    with settings(hide('everything'), warn_only=True):
       return func(cmd).succeeded

