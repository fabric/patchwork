=========
Changelog
=========

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
