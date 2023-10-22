"""
Functions for interrogating a system to determine general attributes.

Specifically, anything that doesn't fit better in other modules where we also
manipulate this information (such as `.packages`). For example, detecting
operating system family and version.
"""

from .files import exists


def distro_name(c):
    """
    Return simple Linux distribution name identifier, e.g. ``"ubuntu"``.

    Uses tools like ``/etc/issue``, and ``lsb_release`` and fits the remote
    system into one of the following:

    * ``fedora``
    * ``rhel``
    * ``centos``
    * ``ubuntu``
    * ``debian``
    * ``other``
    """
    sentinel_files = {
        "centos": ("centos-release",),
        "debian": ("debian_version", "debian_release"),
        "fedora": ("fedora-release",),
        "knoppix": ("knoppix_version"),
        "mint": ("lsb-release"),
        "rhel": ("redhat-release", "redhat_version"),
        "ubuntu": ("lsb-release",),
    }
    for name, sentinels in sentinel_files.items():
        for sentinel in sentinels:
            if exists(c, "/etc/{}".format(sentinel)):
                return name
    return "other"


def distro_family(c):
    """
    Returns basic "family" ID for the remote system's distribution.

    Currently, options include:

    * ``debian``
    * ``redhat``

    If the system falls outside these categories, its specific family or
    release name will be returned instead.
    """
    families = {
        "debian": "debian knoppix mint ubuntu".split(),
        "redhat": "centos fedora rhel".split(),
    }
    distro = distro_name(c)
    for family, members in families.items():
        if distro in members:
            return family
    return distro
