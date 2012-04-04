from fabric.contrib.files import exists


def distro_name():
    """
    Return simple Linux distribution name identifier, e.g. ``"fedora"``.

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
        'fedora': ('fedora-release',)
    }
    for name, sentinels in sentinel_files.iteritems():
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
