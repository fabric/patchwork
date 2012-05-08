"""
Functions for configuring/compiling/installing/packaging source distributions.
"""

import posixpath

from fabric.api import task, sudo, cd, settings

from ..files import directory, exists


@task
def build(name, version, iteration, workdir, uri, force=""):
    """
    Build a package from source, using fpm.

    Keyword arguments:

    * ``name``: Shorthand project/package name. Used both for determining what
      file to download, and what the unpacked directory is expected to be.
      Example: ``"php"``, as found in ``"php-5.4.0.tar.gz"``.
    * ``version``: Upstream release version. Example: ``"5.4.0"``.
    * ``iteration``: Your own version for this build. Usually you'll want to
      increment this every time you're ready to actually distribute the package
      for real. Example: ``3``.
    * ``workdir``: Base working directory. Sources will be unpacked inside of
      it in their own directories, and the staging directory is created as a
      child of this directory as well. Example: ``"/opt/build"``.
    * ``uri``: Download URI. May (and probably should) contain interpolation
      syntax using the following keys:
      
      * ``name``: same as kwarg
      * ``version``: same as kwarg
      * ``package_name``: same as ``"%(name)s-%(version)s"``

      E.g. ``"http://php.net/get/%(package_name)s.tar.bz2/from/us.php.net/mirror"``
      or ``"http://my.mirror/packages/%(name)s/%(name)_%(version)s.tgz"``

    May force a reset to one of the following stages by speciftying ``force``:

    * ``get``: downloading the sources
    * ``configure``: ./configure --flags
    * ``build``: make
    * ``stage``: make install into staging directory
    * ``package``: staging directory => package file

    Stages imply later ones, so force=stage will re-stage *and* re-package.
    """
    package_name = "%s-%s" % (name, version)
    context = {'name': name, 'version': version, 'package_name': package_name}
    uri = uri % context
    source = posixpath.join(workdir, package_name)
    stage = posixpath.join(workdir, 'stage')

    # Handle forcing
    forcing = {}
    force = force.split(',')
    reset = False
    for key in ('get', 'configure', 'build', 'stage', 'package'):
        if key in force:
            reset = True
        forcing[key] = reset

    # Directory
    # TODO: make the chmod an option if users want a "wide open" build dir for
    # manual login user poking around; default to not bothering.
    directory(workdir, mode="777", runner=sudo)
    # Download+unpack
    if forcing['get'] or not exists(source):
        with cd(workdir):
            # TODO: make obtainment process overrideable for users who prefer
            # wget, scp, etc
            sudo("curl -L \"%s\" | tar xjf -" % uri)

    # Configure
    # TODO: configuration options. Do any Python level cleaning (e.g. factoring
    # out --with-x, --with-y into [x, y], ditto for --enable; prefix, etc.)?
    flags = ""
    with cd(source):
        if forcing['configure'] or not exists('Makefile'):
            # If forcing, clean up!
            if forcing['configure']:
                # Is distclean just something I've used with PHP in the past,
                # or does the average make-driven project have it?
                sudo("make distclean")
            sudo("./configure %s" % ' '.join(flags))

        # Build
        # TODO: allow specification of sentinel
        build_sentinel = "file in source dir"
        if forcing['build'] or not exists(build_sentinel):
            sudo("make")

        # Stage
        # TODO: allow specification of sentinel
        stage_sentinel = "file in stage dir"
        if forcing['stage'] or not exists(stage_sentinel):
            with settings(warn_only=True):
                # Nuke if forcing -- e.g. if prefix changed, etc.
                if forcing['stage']:
                    sudo("rm -rf %s" % stage)
                # TODO: allow control over environment of make, e.g. things
                # like INSTALL_ROOT=.
                sudo("make install")

    # Package
    with cd(stage):
        # TODO: handle clean fpm integration somehow. probably have nice Python
        # level handles for the stuff like package name, version, iteration,
        # location, and add a new kwarg for rpm or deb specific things.
        # Main thing that needs doing is constructing an explicit package name
        # and making FPM use it, so one can reliably use that same name format
        # in eg Chef or Puppet.
        package_path = "???"
        if forcing['package'] or not exists(package_path):
            pass

    # TODO: a distribute step? Possibly too user-specific. Or make this a
    # class-based collection of subtasks and let them override that.
