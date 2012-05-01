from fabric.api import sudo, settings, hide


def directory(d, user=None, group=None, mode=None):
    """
    Ensure a directory exists and has given user and/or mode
    """
    sudo("mkdir -p %s" % d)
    if user is not None:
        group = group or user
        sudo("chown %s:%s %s" % (user, group, d))
    if mode is not None:
        sudo("chmod %s %s" % (mode, d))


def exists(path):
    """
    Return True if given path exists on the current remote host.
    """
    cmd = 'test -e "$(echo %s)"' % path
    with settings(hide('everything'), warn_only=True):
        return sudo(cmd).succeeded
