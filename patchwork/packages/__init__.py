from fabric.api import sudo
from patchwork.info import distro_family


def package(*packages):
    """
    Installs one or more ``packages`` using the system package manager.

    Specifically, this function calls a package manager like ``apt-get`` or
    ``yum`` once per package given.
    """
    # Try to suppress interactive prompts, assume 'yes' to all questions
    apt = "DEBIAN_FRONTEND=noninteractive apt-get install -y %s"
    # Run from cache vs updating package lists every time; assume 'yes'.
    yum = "yum install -y %s"
    manager = apt if distro_family() == "debian" else yum
    for package in packages:
        sudo(manager % package)


def rubygem(gem):
    """
    Install a Rubygem
    """
    return sudo("gem install -b --no-rdoc --no-ri %s" % gem)
