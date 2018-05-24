=========
Changelog
=========

- :bug:`-` Fix a bug in `patchwork.transfers.rsync` where it would fail with
  ``AttributeError`` unless your connection had ``connect_kwargs.key_filename``
  defined.
- :bug:`17` Missed some ``.succeeded`` attributes when porting to Fabric 2 -
  they should have been ``.ok``. Patch via Lucio Delelis.
- :release:`1.0.0 <2018-05-08>`
- :feature:`-` Pre-history.
