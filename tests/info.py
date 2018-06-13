from fabric import Result
from mock import patch

from patchwork.info import distro_name, distro_family


class info:

    class distro_name:

        def returns_other_by_default(self, cxn):
            # Sentinels don't exist -> yields default
            # TODO: refactor with module contents in feature branch, eg tease
            # out sentinel file definitions to module level data
            # TODO: make a Session-like thing (or just allow reuse of Session?)
            # that works at this level instead of what it currently does in
            # MockRemote, mocking lower level stuff that is doubtlessly slower
            # and not really necessary?
            cxn.run.return_value = Result(connection=cxn, exited=1)
            assert distro_name(cxn) == "other"

        def returns_fedora_if_fedora_release_exists(self, cxn):

            def fedora_exists(*args, **kwargs):
                # TODO: this is crazy fragile, indicates we want to refactor
                # the guts of exists() or just mock exists() itself instead
                if args[0] == 'test -e "$(echo /etc/fedora-release)"':
                    return Result(connection=cxn, exited=0)
                return Result(connection=cxn, exited=1)

            cxn.run.side_effect = fedora_exists
            assert distro_name(cxn) == "fedora"

        def returns_centos_if_centos_release_exists(self, cxn):

            def centos_exists(*args, **kwargs):
                # TODO: this is crazy fragile, indicates we want to refactor
                # the guts of exists() or just mock exists() itself instead
                if args[0] == 'test -e "$(echo /etc/centos-release)"':
                    return Result(connection=cxn, exited=0)
                return Result(connection=cxn, exited=1)

            cxn.run.side_effect = centos_exists
            assert distro_name(cxn) == "centos"

        # TODO: might as well document & test for the part where we test the
        # sentinels in order, so a system with (somehow) >1 sentinel will
        # appear to be the first one in our list/structure.

    class distro_family:

        @patch("patchwork.info.distro_name")
        def returns_distro_name_when_not_part_of_known_family(
            self, mock_dn, cxn
        ):
            # TODO: do we actually want this behavior? Seems like it'd set one
            # up for backwards compat issues anytime you want to add new family
            # definitions...
            mock_dn.return_value = "no-clue"
            assert distro_family(cxn) == "no-clue"

        @patch("patchwork.info.distro_name")
        def returns_redhat_for_rhel_centos_or_fedora(self, mock_dn, cxn):
            for fake in ("rhel", "centos", "fedora"):
                mock_dn.return_value = fake
                assert distro_family(cxn) == "redhat"

        @patch("patchwork.info.distro_name")
        def returns_debian_for_debian_or_ubuntu(self, mock_dn, cxn):
            for fake in ("debian", "ubuntu"):
                mock_dn.return_value = fake
                assert distro_family(cxn) == "debian"
