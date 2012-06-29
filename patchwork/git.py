from fabric.api import cd, run
from fabric.contrib.files import exists


def clone(repo, path, pull_cmd="git pull"):
    if not exists(path):
        run("git clone %s %s" % (repo, path))
    else:
        with cd(path):
            run(pull_cmd)
