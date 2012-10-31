"""
File transfers, both those using Fabric's put/get, and otherwise.
"""

from fabric.api import local, env, hide
from fabric.network import key_filenames, normalize
from fabric.state import output


def rsync(source, target, exclude=(), delete=False, strict_host_keys=True,
    rsync_opts='', ssh_opts=''):
    """
    Convenient wrapper around your friendly local ``rsync``.

    Specifically, it calls your local ``rsync`` program via a subprocess, and
    fills in its arguments with Fabric's current target host/user/port. It
    provides Python level keyword arguments for some common rsync options, and
    allows you to specify custom options via a string if required (see below.)

    For details on how ``rsync`` works, please see its manpage. ``rsync`` must
    be installed on both your local and remote systems in order for this
    function to work correctly.

    This function makes use of Fabric's ``local()`` function and returns its
    output; thus it will exhibit ``failed``/``succeeded``/``stdout``/``stderr``
    attributes, behaves like a string consisting of ``stdout``, and so forth.

    ``rsync()`` takes the following parameters:

    * ``source``: The local location to copy from. Actually a string passed
      verbatim to ``rsync``, and thus may be a single directory
      (``"my_directory"``) or multiple directories (``"dir1 dir2"``). See the
      ``rsync`` documentation for details.
    * ``target``: The path to sync with on the remote server. Due to how
      ``rsync`` is implemented, the exact behavior depends on the value of
      ``source``:

        * If ``source`` ends with a trailing slash, the files will be
          dropped inside of ``target``. E.g.
          ``rsync("foldername/", "/home/username/project")`` will drop
          the contents of ``foldername`` inside of ``/home/username/project``.
        * If ``source`` does **not** end with a trailing slash,
          ``target`` is effectively the "parent" directory, and a new
          directory named after ``source`` will be created inside of it. So
          ``rsync("foldername", "/home/username")`` would create a new
          directory ``/home/username/foldername`` (if needed) and place the
          files there.

    * ``exclude``: optional, may be a single string, or an iterable of strings,
      and is used to pass one or more ``--exclude`` options to ``rsync``.
    * ``delete``: a boolean controlling whether ``rsync``'s ``--delete`` option
      is used. If True, instructs ``rsync`` to remove remote files that no
      longer exist locally. Defaults to False.
    * ``strict_host_keys``: Boolean determining whether to enable/disable the
      SSH-level option ``StrictHostKeyChecking`` (useful for
      frequently-changing hosts such as virtual machines or cloud instances.)
      Defaults to True.
    * ``rsync_opts``: an optional, arbitrary string which you may use to pass
      custom arguments or options to ``rsync``.
    * ``ssh_opts``: Like ``rsync_opts`` but specifically for the SSH options
      string (rsync's ``--rsh`` flag.)

    This function transparently honors Fabric's port and SSH key
    settings. Calling this function when the current host string contains a
    nonstandard port, or when ``env.key_filename`` is non-empty, will use the
    specified port and/or SSH key filename(s).

    For reference, the approximate ``rsync`` command-line call that is
    constructed by this function is the following::

        rsync [--delete] [--exclude exclude[0][, --exclude[1][, ...]]] \\
            -pthrvz [rsync_opts] <source> <host_string>:<target>

    """
    # Turn single-string exclude into a one-item list for consistency
    if not hasattr(exclude, '__iter__'):
        exclude = (exclude,)
    # Create --exclude options from exclude list
    exclude_opts = ' --exclude "%s"' * len(exclude)
    # Double-backslash-escape
    exclusions = tuple([str(s).replace('"', '\\\\"') for s in exclude])
    # Honor SSH key(s)
    key_string = ""
    keys = key_filenames()
    if keys:
        key_string = "-i " + " -i ".join(keys)
    # Port
    user, host, port = normalize(env.host_string)
    port_string = "-p %s" % port
    # Remote shell (SSH) options
    rsh_string = ""
    # Strict host key checking
    disable_keys = '-o StrictHostKeyChecking=no'
    if not strict_host_keys and disable_keys not in ssh_opts:
        ssh_opts += ' %s' % disable_keys
    rsh_parts = [key_string, port_string, ssh_opts]
    if any(rsh_parts):
        rsh_string = "--rsh='ssh %s'" % " ".join(rsh_parts)
    # Set up options part of string
    options_map = {
        'delete': '--delete' if delete else '',
        'exclude': exclude_opts % exclusions,
        'rsh': rsh_string,
        'extra': rsync_opts
    }
    options = "%(delete)s%(exclude)s -pthrvz %(extra)s %(rsh)s" % options_map
    # Create and run final command string
    if env.host.count(':') > 1:
        # Square brackets are mandatory for IPv6 rsync address,
        # even if port number is not specified
        cmd = "rsync %s %s [%s@%s]:%s" % (options, source, user, host, target)
    else:
        cmd = "rsync %s %s %s@%s:%s" % (options, source, user, host, target)
    return local(cmd)
