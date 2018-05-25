#!/usr/bin/env python

# Support setuptools only, distutils has a divergent and more annoying API and
# few folks will lack setuptools.
from setuptools import setup, find_packages

# Version info -- read without importing
_locals = {}
with open("patchwork/_version.py") as fp:
    exec(fp.read(), None, _locals)
version = _locals["__version__"]

setup(
    name="patchwork",
    version=version,
    description="Deployment/sysadmin operations, powered by Fabric",
    license="BSD",
    long_description=open("README.rst").read(),
    author="Jeff Forcier",
    author_email="jeff@bitprophet.org",
    url="https://fabric-patchwork.readthedocs.io",
    install_requires=["fabric>=2.0,<3.0"],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
        "Topic :: System :: Systems Administration",
    ],
)
