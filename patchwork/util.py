"""
Helpers and decorators, primarily for internal or advanced use.
"""

import textwrap

from functools import wraps
from inspect import getargspec, formatargspec


# TODO: calling all functions as eg directory(c, '/foo/bar/') (with initial c)
# will probably get old; but what's better?
# - Phrasing them as methods on mixin classes to pile on top of Context (so:
# c.directory('/foo/bar/')) pushes us farther towards a god object antipattern,
# though it seems clearly the most practical, especially if we reimplement
# implicit global context;
# - Have each patchwork module as a property of Context itself might help a
# _little_ bit (so it becomes: c.files.directory('/foo/bar/')) but only a
# little, and it almost too-strongly ties us to the module organization (it's
# much easier to change a 'from x import y' than to change a bunch of
# references to a variable)
# - Standalone objects that encapsulate a Context would help to some degree,
# but only in terms of scaling up to many per-module calls (i.e. filemanager =
# files.Manager(c); filemanager.directory('/foo/bar'); if
# filemanager.exists('blah'): xyz; etc) and seems to scale poorly across
# modules (if you want to use eg 1-2 funcs from each module you've got a
# bunch of objects to keep track of)
# - What other patterns are good?

# TODO: how much of the stuff in here should be in Invoke or Fabric core? For
# now, it's ok to leave here because it's highly experimental, but expect a 2.0
# or 3.0 release to see it move elsewhere once patterns are established.


def set_runner(f):
    """
    Set 2nd posarg of decorated function to some callable ``runner``.

    The final value of ``runner`` depends on other args given to the decorated
    function (**note:** *not* the decorator itself!) as follows:

    - By default, ``runner`` is set to the ``run`` method of the first
      positional arg, which is expected to be a `~invoke.context.Context` (or
      subclass). Thus the default runner is `Context.run
      <invoke.context.Context.run>` (or, if the function was given a Fabric
      `~fabric.connection.Connection`, `Connection.run
      <fabric.connection.Connection.run>`).
    - You can override which method on the context is selected, by handing an
      attribute name string to ``runner_method``.
    - Since the common case for overriding the runner is to trigger use of
      `~invoke.context.Context.sudo`, there is a convenient shorthand: giving
      ``sudo=True``.
    - Finally, you may give a callable object to ``runner`` directly, in which
      case nothing special really happens (it's largely as if you called the
      function undecorated, albeit with a kwarg instead of a positional
      argument). This is mostly useful for cases where you're calling one
      decorated function from within another.

    Given this ``function``::

        @set_runner
        def function(c, runner, arg1, arg2=None):
            runner("some command based on arg1 and arg2")

    one may call it without any runner-related arguments, in which case
    ``runner`` ends up being a reference to ``c.run``::

        function(c, "my-arg1", arg2="my-arg2")

    or one may specify ``sudo`` to trigger use of ``c.sudo``::

        function(c, "my-arg1", arg2="my-arg2", sudo=True)

    If one is using a custom Context subclass with other command runner
    methods, one may give ``runner_method`` explicitly::

        class AdminContext(Context):
            def run_admin(self, *args, **kwargs):
                kwargs["user"] = "admin"
                return self.sudo(*args, **kwargs)

        function(AdminContext(), "my-arg1", runner_method="run_admin")

    As noted above, you can always give ``runner`` (as a kwarg) directly to
    avoid most special processing::

        function(c, "my-arg1", runner=some_existing_runner_object)

    .. note::
        If more than one of the ``runner_method``, ``sudo`` or ``runner``
        kwargs are given simultaneously, only one will win, in the following
        order: ``runner``, then ``runner_method``, then ``sudo``.

    .. note::
        As part of the signature modification, `set_runner` also modifies the
        resulting value's docstring as follows:

        - Prepends a Sphinx autodoc compatible signature string, which is
          stripped out automatically on doc builds; see the Sphinx
          ``autodoc_docstring_signature`` setting.
        - Adds trailing ``:param:`` annotations for the extra args as well.
    """

    @wraps(f)
    def inner(*args, **kwargs):
        args = list(args)
        # Pop all useful kwargs (either to prevent clash with real ones, or to
        # remove ones not intended for wrapped function)
        runner = kwargs.pop("runner", None)
        sudo = kwargs.pop("sudo", False)
        runner_method = kwargs.pop("runner_method", None)
        # Figure out what gets applied and potentially overwrite runner
        if not runner:
            method = runner_method
            if not method:
                method = "sudo" if sudo else "run"
            runner = getattr(args[0], method)
        args.insert(1, runner)
        return f(*args, **kwargs)

    inner.__doc__ = munge_docstring(f, inner)
    return inner


def munge_docstring(f, inner):
    # Terrible, awful hacks to ensure Sphinx autodoc sees the intended
    # (modified) signature; leverages the fact that autodoc_docstring_signature
    # is True by default.
    args, varargs, keywords, defaults = getargspec(f)
    # Nix positional version of runner arg, which is always 2nd
    del args[1]
    # Add new args to end in desired order
    args.extend(["sudo", "runner_method", "runner"])
    # Add default values (remembering that this tuple matches the _end_ of the
    # signature...)
    defaults = tuple(list(defaults or []) + [False, "run", None])
    # Get signature first line for Sphinx autodoc_docstring_signature
    sigtext = "{}{}".format(
        f.__name__, formatargspec(args, varargs, keywords, defaults)
    )
    docstring = textwrap.dedent(inner.__doc__ or "").strip()
    # Construct :param: list
    params = """:param bool sudo:
    Whether to run shell commands via ``sudo``.
:param str runner_method:
    Name of context method to use when running shell commands.
:param runner:
    Callable runner function or method. Should ideally be a bound method on the given context object!
"""  # noqa
    return "{}\n{}\n\n{}".format(sigtext, docstring, params)
