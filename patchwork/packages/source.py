"""
Functions for configuring/compiling/installing/packaging source distributions.
"""

import posixpath

from fabric.api import task, run, cd, settings, abort

from ..files import directory, exists
from ..environment import has_binary
from . import package


def _run_step(name, sentinels, forcing):
    sentinel = sentinels.get(name, None)
    sentinel_present = exists(sentinel) if sentinel else False
    return forcing[name] or not sentinel_present


# TODO: maybe break this up into fewer, richer args? e.g. objects or dicts.
# Pro: smaller API
# Con: requires boilerplate for simple stuff
# TODO: great candidate for "collection of tasks" class based approach.
# TODO: also re: each step now looking very similar, at LEAST loop.
@task
def build(name, version, iteration, workdir, uri, enable=(), with_=(),
    flagstr="", dependencies=(), sentinels=None, force="", runner=run):
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

    * ``enable`` and ``with_``: shorthand for adding configure flags. E.g.
      ``build(..., enable=['foo', 'bar'], with_=['biz'])`` results in adding
      the flags ``--enable-foo``, ``--enable-bar`` and ``--with-biz``.
    * ``flagstr``: Arbitrary additional configure flags to add, e.g.
      ``"--no-bad-stuff --with-blah=/usr/blah"``.
    * ``dependencies``: Package names to ensure are installed prior to
      building, using ``package()``.
    * ``sentinels``: Keys are stages, values should be paths to files whose
      existence indicates a successful run of that stage. For each given stage,
      if ``force`` is not set (see below) and its ``sentinel`` value is
      non-empty and the file exists, that stage will automatically be
      skipped.

      Per-stage details:

      * ``"configure"``: Default value for this key is ``"Makefile"``. The
        other stages have no default values.
      * ``"stage"``: The path given here is considered relative to the staging
        directory, not the unpacked source directory.

    May force a reset to one of the following stages by specifying ``force``:

    * ``"get"``: downloading the sources
    * ``"configure"``: ./configure --flags
    * ``"build"``: make
    * ``"stage"``: make install into staging directory
    * ``"package"``: staging directory => package file

    Stages imply later ones, so force=stage will re-stage *and* re-package.
    Forcing will override any sentinel checks.
    """
    package_name = "%s-%s" % (name, version)
    context = {'name': name, 'version': version, 'package_name': package_name}
    uri = uri % context
    source = posixpath.join(workdir, package_name)
    stage = posixpath.join(workdir, 'stage')

    # Make sure we have fpm or the ability to install it
    if not has_binary("fpm"):
        gems = " install Rubygems and then" if not has_binary("gem") else ""
        abort("No fpm found! Please%s 'gem install fpm'." % gems)

    # Default to empty dict (can't use in sig, dicts are mutable)
    sentinels = sentinels or {}
    # Fill in empty configure value
    if 'configure' not in sentinels:
        sentinels['configure'] = "Makefile"

    # Dependencies
    package(*dependencies)

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
    directory(workdir, mode="777", runner=runner)
    # Download+unpack
    if forcing['get'] or not exists(source):
        with cd(workdir):
            # TODO: make obtainment process overrideable for users who prefer
            # wget, scp, etc
            flag = ""
            if uri.endswith((".tar.gz", ".tgz")):
                flag = "z"
            elif uri.endswith((".tar.bz2",)):
                flag = "j"
            runner("curl -L \"%s\" | tar x%sf -" % (uri, flag))

    # Configure
    with_flags = map(lambda x: "--with-%s" % x, with_)
    enable_flags = map(lambda x: "--enable-%s" % x, enable)
    all_flags = " ".join([flagstr] + with_flags + enable_flags)
    with cd(source):
        if _run_step('configure', sentinels, forcing):
            print "++ No Makefile found, running ./configure..."
            # If forcing, clean up!
            if forcing['configure']:
                # TODO: make this configurable, e.g. php 'really' wants
                # distclean for max cleaning, others may too
                # TODO: ties in w/ same call down in build
                runner("make clean")
            runner("./configure %s" % all_flags)
        else:
            print "!! Skipping configure step: %r exists." % sentinels['configure']

        # Build
        if _run_step('build', sentinels, forcing):
            if forcing['build']:
                runner("make clean")
            print "++ No build sentinel or build sentinel not found, running make..."
            runner("make")
        else:
            print "!! Skipping build step: %r exists" % sentinels['build']

        # Stage
        if sentinels.get('stage', None):
            sentinels['stage'] = posixpath.join("..", stage, sentinels['stage'])
        if _run_step('stage', sentinels, forcing):
            print "++ No stage sentinel or stage sentinel not found, running make install..."
            with settings(warn_only=True):
                # Nuke if forcing -- e.g. if --prefix changed, etc.
                # (Otherwise a prefix change would leave both prefixes in the
                # stage, causing problems on actual package install.)
                if forcing['stage']:
                    runner("rm -rf %s" % stage)
                # TODO: allow control over environment of make, e.g. things
                # like INSTALL_ROOT= for apps that don't support DESTDIR
                runner("DESTDIR=%s make install" % stage)
        else:
            print "!! Skipping stage step: %r exists" % sentinels['stage']

    # Package
    with cd(stage):
        # TODO: handle clean fpm integration somehow. probably have nice Python
        # level handles for the stuff like package name, version, iteration,
        # location, and add a new kwarg for rpm or deb specific things.
        # Main thing that needs doing is constructing an explicit package name
        # and making FPM use it, so one can reliably use that same name format
        # in eg Chef or Puppet.
        package_path = "foo"
        if _run_step('package', sentinels, forcing):
            print "++ No package sentinel or package sentinel not found, running fpm..."
            pass
        else:
            print "!! Skipping package step: %r exists" % sentinels['package']


    # TODO: a distribute step? Possibly too user-specific. Or make this a
    # class-based collection of subtasks and let them override that.
