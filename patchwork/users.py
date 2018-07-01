"""Various tasks for verifying user existence and attributes"""

from .util import set_runner


@set_runner
def user_exists(c, runner, user):
    """Returns True if the given system user exists."""
    cmd = "id {}".format(user)
    return runner(cmd, hide=True, warn=True).ok
