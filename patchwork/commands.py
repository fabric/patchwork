"""
Command execution "super-tasks" - combining put/get/run/sudo, etc.
"""
from __future__ import with_statement

import os

from fabric.api import run, put, settings, cd


def run_script(source, cwd, binary='bash', runner=run):
    """
    Invoke local script file ``source`` in remote directory ``cwd``.

    Works by copying the file remotely, executing it, & removing it. Removal
    will always occur even if execution fails.

    :param source: Local path to script file; passed directly to ``fabric.operations.get``.
    :param cwd: Remote working directory to copy to & invoke script from.
    :param binary:
        Command to run remotely with the script as its argument. Defaults to
        ``'bash'``, meaning invocation will be e.g. ``bash myscript.sh``.
    :param runner:
        Fabric function call to use when invoking. Defaults to
        ``fabric.operations.run``.
    :rtype: Return value of the execution call.
    """
    fname = os.path.basename(source)
    put(source, cwd)
    with settings(cd(cwd), warn_only=True):
        result = runner("%s %s" % (binary, fname))
        runner("rm %s" % fname)
    return result
        
