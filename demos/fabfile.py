from fabric.api import task, env
from patchwork import files, info

env.use_ssh_config = True


@task
def create_directory():
    """"Demo: Create a directory """

    files.directory("/tmp/some_directory", user="your_user", group="some_group", mode="g+x")


@task
def create_symlink():
    """ Demo: Creates a symlink """

    files.symlink("/path/to/some/file", "/path/to/symlink")

@task
def get_distro_name():
    """ Demo: Get your distro name """

    name = info.distro_name()
    print(name)