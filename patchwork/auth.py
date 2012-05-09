from fabric.api import sudo, hide

from patchwork.files import append


def _keyfile(who):
    return "/home/%s/.ssh/authorized_keys" % who


def copy_pubkey(from_, to):
    """
    Copy remote user ``from_``'s authorized keys to user ``to``.

    I.e. allow ``from_`` to SSH into the server as ``to``.
    """
    with hide('stdout'):
        append(
            filename=_keyfile(to),
            # Leading newline to ensure keys stay separate
            text=['\n'] + sudo("cat %s" % _keyfile(from_)).splitlines(),
            runner=sudo
        )
