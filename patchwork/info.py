from collections import namedtuple

from fabric.api import run
from environment import has_binary
from fabric.contrib.files import exists
from files import cat


REDHAT_FAMILY_DISTROS = "rhel fedora centos amazon".split()
DEBIAN_FAMILY_DISTROS = "ubuntu debian".split()

# Holder struct for lsb_release info.
lsb_release_info=namedtuple("lsb_release_info", 
        ["lsb_version",
        "distributor",
        "description",
        "release_version",
        "codename"])

def lsb_release():
    """
    Get Linux Standard Base distro information, if available.
    http://refspecs.linuxbase.org/LSB_3.1.1/LSB-Core-generic/LSB-Core-generic/lsbrelease.html

    Returns None if unavailable, or else a lsb_release_info object with the
    following string attributes:
        lsb_version
        distributor
        description
        release_version
        codename
    """
    if not has_binary('lsb_release'):
        return None
    def lsb_attr(flagname):
        return run('lsb_release --short --%s' % flagname).stdout
    result = lsb_release_info(lsb_attr('version'),
            lsb_attr('id'),
            lsb_attr('description'),
            lsb_attr('release'),
            lsb_attr('codename'))
    return result

def distro_name():
    """
    Return simple Linux distribution name identifier, e.g. ``"fedora"``.

    Uses tools like ``/etc/issue``, and ``lsb_release`` and fits the remote
    system into one of the following:

    * ``fedora``
    * ``rhel``
    * ``centos``
    * ``amazon``
    * ``ubuntu``
    * ``debian``
    * ``other``
    """
    lsb_info = lsb_release()
    if lsb_info:
        try:
            distributor_names = {
                    'Ubuntu': 'ubuntu',
                    'Debian': 'debian',
                    'AmazonAMI': 'amazon',
            }
            return distributor_names[lsb_info.distributor]
        except KeyError:
            pass

    sentinel_files = {
        'fedora': ('fedora-release',),
        'centos': ('centos-release',),
    }
    for name, sentinels in sentinel_files.iteritems():
        for sentinel in sentinels:
            if exists('/etc/%s' % sentinel):
                return name

    # Redhat-like distros erratically include /etc/redhat-release
    # instead of distro-specific files.
    redhat_release_file = '/etc/redhat-release'
    if exists(redhat_release_file):
        redhat_release_content = cat(redhat_release_file)
        for distro in REDHAT_FAMILY_DISTROS:
            if distro in redhat_release_content.lower():
                return distro

    system_release_file = '/etc/system-release'
    if exists(system_release_file) and 'Amazon Linux' in cat(system_release_file):
        return 'amazon'

    return "other"


def distro_family():
    """
    Returns basic "family" ID for the remote system's distribution.

    Currently, options include:

    * ``debian``
    * ``redhat``
    
    If the system falls outside these categories, its discovered distro_name
    will be returned instead (possibly ``other`` if its type couldn't be
    determined).
    """
    families = {
        'debian': "debian ubuntu".split(),
        'redhat': "rhel centos fedora amazon".split()
    }
    distro = distro_name()
    for family, members in families.iteritems():
        if distro in members:
            return family
    # Even if we haven't been able to determine exact distro,
    # we may be able to determine the overall family.
    if distro == 'other':
        if exists('/etc/debian_version'):
            return 'debian'
    return distro
