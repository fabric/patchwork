from fabric.api import run, settings, hide


def directory(d, user=None, group=None, mode=None, runner=run):
    """
    Ensure a directory exists and has given user and/or mode
    """
    runner("mkdir -p %s" % d)
    if user is not None:
        group = group or user
        runner("chown %s:%s %s" % (user, group, d))
    if mode is not None:
        runner("chmod %s %s" % (mode, d))


def exists(path, runner=run):
    """
    Return True if given path exists on the current remote host.
    """
    cmd = 'test -e "$(echo %s)"' % path
    with settings(hide('everything'), warn_only=True):
        return runner(cmd).succeeded
