from invoke import Context

from patchwork.util import set_runner


class util:

    class set_runner_:
        # NOTE: using runner == c.run/whatever in these tests because 'is' is
        # always False for some reason despite both args being the same object,
        # same id() etc. Not sure wtf. Probably my fault somehow.
        def defaults_to_run(self):

            @set_runner
            def myfunc(c, runner):
                assert runner == c.run

            myfunc(Context())

        def does_not_tweak_other_args(self):

            @set_runner
            def myfunc(c, runner, other, args="values", default="default"):
                assert isinstance(c, Context)
                assert runner == c.run
                assert other == "otherval"
                assert args == "override"
                assert default == "default"

            myfunc(Context(), "otherval", args="override")

        def allows_overriding_runner_method(self):

            @set_runner
            def myfunc(c, runner, other, args="values", default="default"):
                assert isinstance(c, Context)
                assert runner == c.sudo
                assert other == "otherval"
                assert args == "override"
                assert default == "default"

            myfunc(
                Context(), "otherval", args="override", runner_method="sudo"
            )

        def sudo_is_bool_shorthand_for_sudo_runner(self):

            @set_runner
            def myfunc(c, runner, other, args="values", default="default"):
                assert isinstance(c, Context)
                assert runner == c.sudo
                assert other == "otherval"
                assert args == "override"
                assert default == "default"

            myfunc(Context(), "otherval", args="override", sudo=True)

        def may_give_runner_directly_for_no_magic(self):

            def whatever():
                pass

            @set_runner
            def myfunc(c, runner, other, args="values", default="default"):
                assert isinstance(c, Context)
                assert runner is whatever
                assert other == "otherval"
                assert args == "override"
                assert default == "default"

            myfunc(Context(), "otherval", args="override", runner=whatever)

        def runner_wins_over_runner_method(self):

            def whatever():
                pass

            @set_runner
            def myfunc(c, runner):
                assert runner is whatever

            myfunc(Context(), runner=whatever, runner_method="run")

        def runner_wins_over_sudo(self):

            def whatever():
                pass

            @set_runner
            def myfunc(c, runner):
                assert runner is whatever

            myfunc(Context(), runner=whatever, sudo=True)

        def runner_method_wins_over_sudo(self):

            @set_runner
            def myfunc(c, runner):
                assert runner == c.run

            myfunc(Context(), runner_method="run", sudo=True)
