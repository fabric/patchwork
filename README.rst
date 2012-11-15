Patchwork is a Python (2.6+) toolkit for common Unix deployment and sysadmin
operations, such as "install package", "create directory with X owner", etc.

For those familiar with configuration management tools like Chef or Puppet,
this library is similar to a standalone version of their "Resources". Unlike
those frameworks, however, Patchwork does not presume to tell you *how* to use
these components -- you can use them in deploy scripts, system management
tools, or even to build your own Chef or Puppet level system.

Patchwork is implemented on top of the `Fabric <http://fabfile.org>`_
high-level SSH module.

You can install the `development version
<https://github.com/fabric/patchwork/tarball/master#egg=patchwork-dev>`_ via
``pip install patchwork==dev`` or ``pip install -e
git+https://github.com/fabric/patchwork@master#egg=patchwork-dev``.
