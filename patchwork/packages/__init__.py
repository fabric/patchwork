"""
Management of various (usually binary) package types - OS, language, etc.
"""

# TODO: intent is to have various submodules for the various package managers -
# apt/deb, rpm/yum/dnf, arch/pacman, etc etc etc.


from patchwork.info import distro_family


def package(c, *packages):
    """
    Installs one or more ``packages`` using the system package manager.

    Specifically, this function calls a package manager like ``apt-get`` or
    ``yum`` once per package given.
    """
    # Try to suppress interactive prompts, assume 'yes' to all questions
    apt = "DEBIAN_FRONTEND=noninteractive apt-get install -y {}"
    # Run from cache vs updating package lists every time; assume 'yes'.
    yum = "yum install -y %s"
    manager = apt if distro_family(c) == "debian" else yum
    for package in packages:
        c.sudo(manager.format(package))


def rubygem(c, gem):
    """
    Install a Ruby gem.
    """
    return c.sudo("gem install -b --no-rdoc --no-ri {}".format(gem))
