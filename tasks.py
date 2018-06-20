from importlib import import_module

from invocations import docs, travis
from invocations.checks import blacken
from invocations.packaging import release
from invocations.pytest import test, coverage

from invoke import Collection, task


@task
def sanity(c):
    """
    Quick sanity check to ensure we're installed successfully. Mostly for CI.
    """
    # Doesn't need to literally import everything, but "a handful" will do.
    for name in ("environment", "files", "transfers"):
        mod = "patchwork.{}".format(name)
        import_module(mod)
        print("Imported {} successfully".format(mod))


ns = Collection(docs, release, travis, test, coverage, sanity, blacken)
ns.configure(
    {
        "packaging": {
            "sign": True,
            "wheel": True,
            "check_desc": True,
            "changelog_file": "docs/changelog.rst",
        }
    }
)
