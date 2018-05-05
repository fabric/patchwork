=====
About
=====

Patchwork is a mid-level library of Unix system administration primitives such
as "install package" or "create user account", plus related functions for
things like introspecting a target system's operating system.  Specifically:

* Primary API calls strive to be **idempotent**: they may be called multiple
  times in a row without unwanted changes piling up or causing errors.
* Patchwork **is just an API**:  it has no concept of "recipes", "manifests",
  "classes", "roles" or other high level organizational units. This is left up
  to the user or wrapping libraries.
    * This is one way Patchwork differs from larger configuration management
      frameworks like `Chef <http://opscode.com/chef/>`_ or `Puppet
      <http://puppetlabs.com>`_. Patchwork is closest in nature to those tools'
      "resources."
* It is implemented in **shell calls**, typically sent **over SSH** via the `Fabric
  <http://fabfile.org>`_ library from a local workstation -- though where
  possible, its functions expect a baseline Invoke `~invoke.context.Context`
  object and can thus run locally or remotely, depending on the specific
  context supplied by the caller.


===============
API description
===============

* `info`: Information-gathering methods, e.g. "give me a label for the
  OS."
    * OS type
    * Network interfaces
    * Other stuff Facter/Ohai do?
* `packages`: Install/remove/manipulate system-level software packages
    * `__init__`: Generic install/etc stuff, which switches on OS in the background
    * `apt`: Debian/APT stuff, e.g. debconf, Ubuntu PPAs etc
    * `rpm`: RedHat/RPM stuff, e.g. yum repos
* `files`: Create/remove/modify files, symlinks and directories
    * Including "download this URL directly to the remote end", etc
* `auth`: Create/manage users, groups, `sudoers` etc
* `vcs`: Manage version control checkouts
* `commands`: Execute complicated tasks combining run/sudo/get/put and so
  forth, such as uploading/running/removing script files.

Stuff that might want to live in some sort of plugin/ext system?)

* `python`: Manage pip, virtualenv (and Python installation?)
