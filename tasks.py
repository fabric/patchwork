from __future__ import unicode_literals, print_function

from importlib import import_module

from invocations import docs, travis
from invocations.packaging import release
from invocations.pytest import test

from invoke import Collection, task


@task
def sanity(c):
    """
    Quick sanity check to ensure we're installed successfully. Mostly for CI.
    """
    # Doesn't need to literally import everything, but "a handful" will do.
    for name in ('environment', 'files', 'transfers'):
        import_module("patchwork.{}".format(name))
    print("\U0001F44D") # FUN WITH UNICODE


ns = Collection(docs, release, travis, test, sanity)
ns.configure({
    'packaging': {
        'sign': True,
        'wheel': True,
        'check_desc': True,
    },
})
