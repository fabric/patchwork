"""
Functions for configuring/compiling/installing/packaging source distributions.
"""

import posixpath

from fabric.api import run, cd, settings, abort

from ..files import directory, exists
from ..environment import has_binary
from . import package


def _run_step(name, forcing, sentinel=None):
    sentinel_present = exists(sentinel) if sentinel else False
    return forcing[name] or not sentinel_present

_go_msg = "++ %s: forced or sentinel missing, running..."

def clean(runner):
    runner("make clean")

def install(runner, stage_root):
    runner("DESTDIR=%s make install" % stage_root)


# TODO: maybe break this up into fewer, richer args? e.g. objects or dicts.
# Pro: smaller API
# Con: requires boilerplate for simple stuff
# TODO: great candidate for "collection of tasks" class based approach.
# TODO: also re: each step now looking very similar, at LEAST loop.
def build(name, version, iteration, workdir, uri, type_, enable=(), with_=(),
    flagstr="", dependencies=(), sentinels=None, clean=clean, install=install,
    force="", runner=run):
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

    * ``type``: Package type to build. Passed directly to ``fpm``, so should be
      e.g. ``"deb"``, ``"rpm"`` etc.
    * ``enable`` and ``with_``: shorthand for adding configure flags. E.g.
      ``build(..., enable=['foo', 'bar'], with_=['biz'])`` results in adding
      the flags ``--enable-foo``, ``--enable-bar`` and ``--with-biz``.
    * ``flagstr``: Arbitrary additional configure flags to add, e.g.
      ``"--no-bad-stuff --with-blah=/usr/blah"``.
    * ``dependencies``: Package names to ensure are installed prior to
      building, using ``package()``.
    * ``sentinels``: Keys are steps, values should be paths (relative to the
      source directory unless otherwise specified) to files whose existence
      indicates a successful run of that step. For each given step, if
      ``force`` is not set (see below) and its ``sentinel`` value is non-empty
      and the file exists, that step will automatically be skipped.

      Per-step details:

      * ``"configure"``: Default value for this key is ``"Makefile"``. The
        other steps have no default values.
      * ``"stage"``: The path given here is considered relative to the staging
        directory, not the unpacked source directory.
      * ``"package"``: The path given here should be relative to ``workdir``.

    * ``clean``: Callback (given ``runner``) to execute when cleaning is
      needed. Defaults to a function that calls ``runner("make clean")``.
    * ``install``: Callback (given ``runner`` and ``stage_root``) to execute as
      the "install" step. Defaults to a function that calls
      ``runner("DESTDIR=<stage_root> make install")``

    May force a reset to one of the following steps by specifying ``force``:

    * ``"get"``: downloading the sources
    * ``"configure"``: ./configure --flags
    * ``"build"``: make
    * ``"stage"``: make install into staging directory
    * ``"package"``: staging directory => package file

    steps imply later ones, so force=stage will re-stage *and* re-package.
    Forcing will override any sentinel checks.
    """
    package_name = "%s-%s" % (name, version)
    context = {'name': name, 'version': version, 'package_name': package_name}
    uri = uri % context
    source = posixpath.join(workdir, package_name)
    stage = posixpath.join(workdir, 'stage')

    # Make sure we have fpm or the ability to install it
    # TODO: allow actual, non-staged make install which then doesn't need fpm
    # or the package/distribute steps.
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
            if any([x in uri for x in (".tar.gz", ".tgz")]):
                flag = "z"
            elif any([x in uri for x in (".tar.bz2",)]):
                flag = "j"
            runner("curl -L \"%s\" | tar x%sf -" % (uri, flag))

    # Configure
    with_flags = map(lambda x: "--with-%s" % x, with_)
    enable_flags = map(lambda x: "--enable-%s" % x, enable)
    all_flags = " ".join([flagstr] + with_flags + enable_flags)
    with cd(source):
        # If forcing configure or build, clean up first. Leftover artifacts
        # from bad builds can be seriously annoying, especially if they don't
        # cause outright problems.
        if forcing['configure'] and exists('Makefile'):
            clean(runner)
        if _run_step('configure', forcing, sentinels['configure']):
            print _go_msg % 'configure'
            runner("./configure %s" % all_flags)
        else:
            print "!! Skipping configure step: %r exists." % sentinels['configure']

        # Build
        if _run_step('build', forcing, sentinels['build']):
            print _go_msg % 'build'
            runner("make")
        else:
            print "!! Skipping build step: %r exists" % sentinels['build']

        # Stage
        stage_sentinel = sentinels['stage']
        if stage_sentinel is not None:
            stage_sentinel = posixpath.join("..", stage, sentinels['stage'])
        if _run_step('stage', forcing, stage_sentinel):
            print _go_msg % 'stage'
            with settings(warn_only=True):
                # Nuke if forcing -- e.g. if --prefix changed, etc.
                # (Otherwise a prefix change would leave both prefixes in the
                # stage, causing problems on actual package install.)
                if forcing['stage']:
                    runner("rm -rf %s" % stage)
                install(runner=runner, stage_root=stage)
        else:
            print "!! Skipping stage step: %r exists" % sentinels['stage']

    with cd(workdir):
        do_package = _run_step('package', forcing, sentinels['package'])

    with cd(stage):
        # TODO: handle clean fpm integration somehow. probably have nice Python
        # level handles for the stuff like package name, version, iteration,
        # location, and add a new kwarg for rpm or deb specific things.
        # Main thing that needs doing is constructing an explicit package name
        # and making FPM use it, so one can reliably use that same name format
        # in eg Chef or Puppet.
        if do_package:
            print _go_msg % 'package'
            # --package <workdir> to control where package actually goes.
            # Filename format will be the default for the given output type.
            # Target directory is '.' since we're cd'd to stage root. Will then
            # work OK for any potential --prefix the user may have given.
            runner(r"""fpm \
                    -s dir \
                    -t %(type_)s \
                    --name %(name)s \
                    --version %(version)s \
                    --iteration %(iteration)s \
                    --package %(workdir)s \
                    .
            """ % locals()) # Yea, yea. Bite me.
        else:
            print "!! Skipping package step: %r exists" % sentinels['package']


    # TODO: a distribute step? Possibly too user-specific. Or make this a
    # class-based collection of subtasks and let them override that.
