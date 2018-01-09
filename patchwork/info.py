from fabric.api import run, hide
from fabric.contrib.files import exists
from patchwork.environment import has_binary


def distro_name():
    """
    Return simple Linux distribution name identifier, e.g. ``"fedora"``.

    Uses files like ``/etc/os-release`` (or ``/etc/*-release``) and
    tools like ``/etc/issue``, and ``lsb_release``, trying to identify
    short id of the system. Examples:

    * ``fedora``
    * ``rhel``
    * ``centos``
    * ``ubuntu``
    * ``debian``
    * ``other``
    """
    with hide('running', 'stdout'):
        if has_binary('lsb_release'):
            distro_id = run('lsb_release -s -i').strip().lower()
            if distro_id:
                return distro_id

        if exists('/etc/lsb-release'):
            distro_id = run('''awk -F '=' '$1 == "DISTRIB_ID" \
                {print $2; exit }' \
                /etc/lsb-release ''',
            shell=False).strip().lower()
            if distro_id:
                return distro_id

        if exists('/etc/os-release'):
            distro_id = run('''awk -F '=' '$1 == "ID" \
                {print $2; exit }' \
                /etc/os-release''',
            shell=False).strip().lower()
            if distro_id:
                return distro_id

    # and now the fallback method (guess by existing files)
    sentinel_files = (
        ('fedora', ('fedora-release',)),
        ('centos', ('centos-release',)),
        ('debian', ('debian_version',)),
        ('gentoo', ('gentoo-release',)),
    )

    for name, sentinels in sentinel_files:
        for sentinel in sentinels:
            if exists('/etc/%s' % sentinel):
                return name
    return "other"


def distro_family():
    """
    Returns basic "family" ID for the remote system's distribution.

    Currently, options include:

    * ``debian``
    * ``redhat``

    If the system falls outside these categories, its specific family or
    release name will be returned instead.
    """
    families = {
        'debian': "debian ubuntu".split(),
        'redhat': "rhel centos fedora".split()
    }
    distro = distro_name()
    for family, members in families.iteritems():
        if distro in members:
            return family
    return distro
