Patchwork is a mid-level library of Unix system administration primitives such
as "install package" or "create user account", interrogative functionality for
introspecting system state, and other commonly useful functions built on top of
the `Fabric <http://fabfile.org>`_ library.

Specifically:

- Primary API calls strive to be **idempotent**: they may be called multiple
  times in a row without unwanted changes piling up or causing errors.
- Patchwork **is just an API**:  it has no concept of "recipes", "manifests",
  "classes", "roles" or other high level organizational units. This is left up
  to the user or wrapping libraries.

    - This is one way Patchwork differs from larger configuration management
      frameworks like `Chef <http://opscode.com/chef/>`_ or `Puppet
      <http://puppetlabs.com>`_. Patchwork is closest in nature to those tools'
      "resources."

- It is implemented in **shell calls**, typically sent **over SSH** from a
  local workstation.

    - However, where possible, its functions expect a baseline Invoke
      `~invoke.context.Context` object and can thus run locally *or* remotely,
      depending on the specific context supplied by the caller.
