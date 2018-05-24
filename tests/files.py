from mock import call

from patchwork.files import directory


class files:

    class directory_:

        def base_case_creates_dir_with_dash_p(self, cxn):
            directory(cxn, "/some/dir")
            cxn.run.assert_called_once_with("mkdir -p /some/dir")

        def user_sets_owner_and_group(self, cxn):
            directory(cxn, "/some/dir", user="user")
            cxn.run.assert_any_call("chown user:user /some/dir")

        def group_may_be_given_to_change_group(self, cxn):
            directory(cxn, "/some/dir", user="user", group="admins")
            cxn.run.assert_any_call("chown user:admins /some/dir")

        def mode_adds_a_chmod(self, cxn):
            directory(cxn, "/some/dir", mode="0700")
            cxn.run.assert_any_call("chmod 0700 /some/dir")

        def all_args_in_play(self, cxn):
            directory(
                cxn, "/some/dir", user="user", group="admins", mode="0700"
            )
            assert cxn.run.call_args_list == [
                call("mkdir -p /some/dir"),
                call("chown user:admins /some/dir"),
                call("chmod 0700 /some/dir"),
            ]
