from functools import wraps


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


# TODO: is it possible to both expose the wrapped function's signature to
# Sphinx autodoc AND remain a signature-altering decorator? =/ Using @decorator
# is nice but it is only for signature-PRESERVING decorators. We really want a)
# prevent users from having to phrase runner as 'runner=None', and b) the
# convenience of sudo=True...but that means signature-altering.
# TODO: this may be another spot where we want to reinstate fabric 1's docs
# unwrap function.
def set_runner(f):
    """
    Set 2nd posarg of decorated function to some callable ``runner``.

    The final value of ``runner`` depends on other args given to the decorated
    function (**note:** *not* the decorator itself!) as follows:

    - By default, you can simply ignore the decorated function's ``runner``
      argument entirely, in which case it will end up being set to the ``run``
      method on the first positional arg (expected to be a
      `~invoke.context.Context` and thus, the default value is `Context.run
      <invoke.context.Context.run>`).
    - You can override which method on that object is selected, by handing an
      attribute name string to ``runner_method``.
    - Since the common case for this functionality is to trigger use of
      `~invoke.context.Context.sudo`, there is a convenient shorthand, setting
      ``sudo=True``.
    - Finally, you may give a callable object to ``runner`` directly, in which
      case nothing special really happens (it's largely as if you called the
      function undecorated). This is useful for cases where you're calling one
      decorated function from within another.

    .. note::
        The ``runner_method`` and ``sudo`` kwargs exist only at the decorator
        level, and are not passed into the decorated function.

    .. note::
        If more than one of the above kwargs is given at the same time, only
        one will win, in the following order: ``runner``, then
        ``runner_method``, then ``sudo``.

    As an example, given this example ``function``::

        @set_runner
        def function(c, runner, arg1, arg2=None):
            runner("some command based on arg1 and arg2")

    One may call it without any runner-related arguments, in which case
    ``runner`` ends up being a reference to ``c.run``::

        function(c, "my-arg1", arg2="my-arg2")

    Or one may specify ``sudo`` to trigger use of ``c.sudo``::

        function(c, "my-arg1", arg2="my-arg2", sudo=True)

    If one is using a custom Context subclass with other command runner
    methods, one may give ``runner_method`` explicitly::

        class AdminContext(Context):
            def run_admin(self, *args, **kwargs):
                kwargs['user'] = 'admin'
                return self.sudo(*args, **kwargs)

        function(AdminContext(), "my-arg1", runner_method='run_admin')

    Finally, to reiterate, you can always give ``runner`` directly to avoid any
    special processing (though be careful not to get mixed up - if this runner
    isn't actually a method on the ``c`` context object, debugging could be
    frustrating!)::

        function(c, "my-arg1", runner=some_existing_runner_object)
    """
    @wraps(f)
    def inner(*args, **kwargs):
        args = list(args)
        # Pop all useful kwargs (either to prevent clash with real ones, or to
        # remove ones not intended for wrapped function)
        runner = kwargs.pop('runner', None)
        sudo = kwargs.pop('sudo', False)
        runner_method = kwargs.pop('runner_method', None)
        # Figure out what gets applied and potentially overwrite runner
        if not runner:
            method = runner_method
            if not method:
                method = 'sudo' if sudo else 'run'
            runner = getattr(args[0], method)
        args.insert(1, runner)
        return f(*args, **kwargs)
    return inner
