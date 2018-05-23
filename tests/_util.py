from mock import Mock
from invoke import Context


class MockedContext(object):

    def setup(self):
        # TODO: use MockContext if we care about supplying mocked results of
        # run()/etc calls. For now we only care about what's being put INTO
        # run() and friends, for which MockContext isn't as useful.
        self.c = Context()
        self.c.run = Mock()
        self.c.sudo = Mock()
