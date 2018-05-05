=========
Patchwork
=========

.. include:: ../README.rst


===============
API description
===============

- ``info``: Information-gathering methods, e.g. "give me a label for the
  OS."

    - OS type
    - Network interfaces
    - Other stuff Facter/Ohai do?

- ``packages``: Install/remove/manipulate system-level software packages

    - ``__init__``: Generic install/etc stuff, which switches on OS in the background
    - ``apt``: Debian/APT stuff, e.g. debconf, Ubuntu PPAs etc
    - ``rpm``: RedHat/RPM stuff, e.g. yum repos

- ``files``: Create/remove/modify files, symlinks and directories

    - Including "download this URL directly to the remote end", etc

- ``auth``: Create/manage users, groups, ``sudoers`` etc
- ``vcs``: Manage version control checkouts
- ``commands``: Execute complicated tasks combining run/sudo/get/put and so
  forth, such as uploading/running/removing script files.
- ``python``: Manage pip, virtualenv (and Python installation?)
