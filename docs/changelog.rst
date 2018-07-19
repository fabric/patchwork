=========
Changelog
=========

- :support:`-` Publicly document the `.util` module and its `~.util.set_runner`
  decorator, which decorates the functions in the `.files` module (and any
  future applicable modules) allowing users to specify extra arguments like
  ``sudo=True`` or ``runner_method="local"``.

  As part of publicizing this, we added some docstring mutation to the
  decorator so returned objects expose Sphinx autodoc hints and parameter
  lists. This should replace the ``function(*args, **kwargs)`` signatures that
  used to end up in the rendered documentation.
- :support:`-` Add parameter lists to the members of the `.files` module.
- :release:`1.0.1 <2018-06-20>`
- :bug:`23` Fix some outstanding Python 2-isms (use of ``iteritems``) in
  `.info.distro_name` and `.info.distro_family`, as well as modules which
  imported those -- such as `.packages`.

  Includes adding some basic tests for this functionality as well. Thanks to
  ``@ChaoticMind`` for the report.
- :bug:`20` (via :issue:`21`) `patchwork.transfers.rsync` didn't handle its
  ``exclude`` parameter correctly when building the final ``rsync`` command (it
  came out looking like a stringified tuple). Fixed by Kegan Gan.
- :bug:`-` Fix a bug in `patchwork.transfers.rsync` where it would fail with
  ``AttributeError`` unless your connection had ``connect_kwargs.key_filename``
  defined.
- :bug:`17` Missed some ``.succeeded`` attributes when porting to Fabric 2 -
  they should have been ``.ok``. Patch via Lucio Delelis.
- :release:`1.0.0 <2018-05-08>`
- :feature:`-` Pre-history.
