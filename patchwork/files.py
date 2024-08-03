"""
Tools for file and directory management.
"""

import re

from .util import set_runner


@set_runner
def directory(c, runner, path, user=None, group=None, mode=None):
    """
    Ensure a directory exists and has given user and/or mode

    :param c:
        `~invoke.context.Context` within to execute commands.
    :param str path:
        File path to directory.
    :param str user:
        Username which should own the directory.
    :param str group:
        Group which should own the directory; defaults to ``user``.
    :param str mode:
        ``chmod`` compatible mode string to apply to the directory.
    """
    runner("mkdir -p {}".format(path))
    if user is not None:
        group = group or user
        runner("chown {}:{} {}".format(user, group, path))
    if mode is not None:
        runner("chmod {} {}".format(mode, path))


@set_runner
def exists(c, runner, path):
    """
    Return True if given path exists on the current remote host.

    :param c:
        `~invoke.context.Context` within to execute commands.
    :param str path:
        Path to check for existence.
    """
    cmd = 'test -e "$(echo {})"'.format(path)
    return runner(cmd, hide=True, warn=True).ok


@set_runner
def contains(c, runner, filename, text, exact=False, escape=True):
    """
    Return True if ``filename`` contains ``text`` (which may be a regex.)

    By default, this function will consider a partial line match (i.e. where
    ``text`` only makes up part of the line it's on). Specify ``exact=True`` to
    change this behavior so that only a line containing exactly ``text``
    results in a True return value.

    This function leverages ``egrep`` on the remote end, so it may not follow
    Python regular expression syntax perfectly.

    If ``escape`` is False, no extra regular expression related escaping is
    performed (this includes overriding ``exact`` so that no ``^``/``$`` is
    added.)

    :param c:
        `~invoke.context.Context` within to execute commands.
    :param str filename:
        File path within which to check for ``text``.
    :param str text:
        Text to search for.
    :param bool exact:
        Whether to expect an exact match.
    :param bool escape:
        Whether to perform regex-oriented escaping on ``text``.
    """
    if escape:
        text = _escape_for_regex(text)
        if exact:
            text = "^{}$".format(text)
    egrep_cmd = 'egrep "{}" "{}"'.format(text, filename)
    return runner(egrep_cmd, hide=True, warn=True).ok


@set_runner
def append(c, runner, filename, text, partial=False, escape=True):
    """
    Append string (or list of strings) ``text`` to ``filename``.

    When a list is given, each string inside is handled independently (but in
    the order given.)

    If ``text`` is already found in ``filename``, the append is not run, and
    None is returned immediately. Otherwise, the given text is appended to the
    end of the given ``filename`` via e.g. ``echo '$text' >> $filename``.

    The test for whether ``text`` already exists defaults to a full line match,
    e.g. ``^<text>$``, as this seems to be the most sensible approach for the
    "append lines to a file" use case. You may override this and force partial
    searching (e.g. ``^<text>``) by specifying ``partial=True``.

    Because ``text`` is single-quoted, single quotes will be transparently
    backslash-escaped. This can be disabled with ``escape=False``.

    :param c:
        `~invoke.context.Context` within to execute commands.
    :param str filename:
        File path to append onto.
    :param str text:
        Text to append.
    :param bool partial:
        Whether to test partial line matches when determining if appending is
        necessary.
    :param bool escape:
        Whether to perform regex-oriented escaping on ``text``.
    """
    # Normalize non-list input to be a list
    if isinstance(text, str):
        text = [text]
    for line in text:
        regex = "^" + _escape_for_regex(line) + ("" if partial else "$")
        if (
            line
            and exists(c, filename, runner=runner)
            and contains(c, filename, regex, escape=False, runner=runner)
        ):
            continue
        line = line.replace("'", r"'\\''") if escape else line
        runner("echo '{}' >> {}".format(line, filename))


def _escape_for_regex(text):
    """Escape ``text`` to allow literal matching using egrep"""
    regex = re.escape(text)
    # Seems like double escaping is needed for \
    regex = regex.replace("\\\\", "\\\\\\")
    # Triple-escaping seems to be required for $ signs
    regex = regex.replace(r"\$", r"\\\$")
    # Whereas single quotes should not be escaped
    regex = regex.replace(r"\'", "'")
    return regex
