"""
Shell environment introspection, e.g. binaries in effective $PATH, etc.
"""

from fabric.api import run, settings, hide


def has_binary(name, runner=run):
    with settings(hide('everything'), warn_only=True):
        return runner("which %s" % name).succeeded
