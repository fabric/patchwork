from mock import call

from patchwork.files import directory

from _util import MockedContext


class files(MockedContext):

    class directory_:

        def base_case_creates_dir_with_dash_p(self):
            directory(self.c, "/some/dir")
            self.c.run.assert_called_once_with("mkdir -p /some/dir")

        def user_sets_owner_and_group(self):
            directory(self.c, "/some/dir", user="user")
            self.c.run.assert_any_call("chown user:user /some/dir")

        def group_may_be_given_to_change_group(self):
            directory(self.c, "/some/dir", user="user", group="admins")
            self.c.run.assert_any_call("chown user:admins /some/dir")

        def mode_adds_a_chmod(self):
            directory(self.c, "/some/dir", mode="0700")
            self.c.run.assert_any_call("chmod 0700 /some/dir")

        def all_args_in_play(self):
            directory(
                self.c, "/some/dir", user="user", group="admins", mode="0700"
            )
            assert self.c.run.call_args_list == [
                call("mkdir -p /some/dir"),
                call("chown user:admins /some/dir"),
                call("chmod 0700 /some/dir"),
            ]
