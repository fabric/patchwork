from mock import call, patch

from patchwork.files import directory, append, contains


class files:

    class directory_:

        def base_case_creates_dir_with_dash_p(self, cxn):
            directory(cxn, "/some/dir")
            cxn.run.assert_called_once_with('mkdir -p "/some/dir"')

        def creates_dir_with_double_quotes(self, cxn):
            directory(cxn, '/some/double"quote')
            cxn.run.assert_called_once_with('mkdir -p "/some/double\\"quote"')

        def user_sets_owner_and_group(self, cxn):
            directory(cxn, "/some/dir", user="user")
            cxn.run.assert_any_call('chown "user:user" "/some/dir"')

        def group_may_be_given_to_change_group(self, cxn):
            directory(cxn, "/some/dir", user="user", group="admins")
            cxn.run.assert_any_call('chown "user:admins" "/some/dir"')

        def mode_adds_a_chmod(self, cxn):
            directory(cxn, "/some/dir", mode="0700")
            cxn.run.assert_any_call('chmod "0700" "/some/dir"')

        def all_args_in_play(self, cxn):
            directory(
                cxn, "/some/dir", user="user", group="admins", mode="0700"
            )
            assert cxn.run.call_args_list == [
                call('mkdir -p "/some/dir"'),
                call('chown "user:admins" "/some/dir"'),
                call('chmod "0700" "/some/dir"'),
            ]

        def contains_issue34(self, cxn):
            contains(cxn, "/some/file", "'*'")
            cxn.run.assert_any_call(
                r'''egrep "'\\*'" "/some/file"''',
                hide=True, warn=True
            )

        def contains_trailing_dollar(self, cxn):
            contains(cxn, "/some/file", "trailing $")
            cxn.run.assert_called_once_with(
                r'egrep "trailing \\\$" "/some/file"',
                hide=True, warn=True
            )

        def contains_trailing_backslash(self, cxn):
            contains(cxn, "/some/file", "trailing \\")
            cxn.run.assert_called_once_with(
                r'egrep "trailing \\\\" "/some/file"',
                hide=True, warn=True
            )

        @patch('patchwork.files.contains')
        def append_ending_single_quote(self, m, cxn):
            m.return_value = False
            append(cxn, "/some/file", "alias l='ls -rtl'")
            cxn.run.assert_any_call(
                'echo \'alias l=\'\\\'\'ls -rtl\'\\\'\'\' >> "/some/file"'
            )

        @patch('patchwork.files.contains')
        def append_trailing_dollar(self, m, cxn):
            m.return_value = False
            append(cxn, "/some/file", "trailing $")
            cxn.run.assert_any_call(
                r'''echo 'trailing $' >> "/some/file"''',
            )

        @patch('patchwork.files.contains')
        def append_trailing_backslash(self, m, cxn):
            m.return_value = False
            append(cxn, "/some/file", "trailing \\")

            assert cxn.run.call_args_list == [
                call('test -e "$(echo /some/file)"', hide=True, warn=True),
                call(r'''echo 'trailing \' >> "/some/file"''')
            ]


        @patch('patchwork.files.contains')
        def append_trailing_backtick(self, m, cxn):
            m.return_value = False
            append(cxn, "/some/file", "trailing `")
            cxn.run.assert_any_call(
                r'''echo 'trailing `' >> "/some/file"'''
            )

        @patch('patchwork.files.contains')
        def append_issue_34(self, m, cxn):
            m.return_value = False
            append(cxn, "/some/file", "listen_addresses='*'", escape=True)
            cxn.run.assert_any_call(
                'echo \'listen_addresses=\'\\\'\'*\'\\\'\'\' >> "/some/file"'
            )
