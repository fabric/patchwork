#!/usr/bin/env python

# Would love to use distutils but fuck manually keeping a list of all my
# subpackages by hand :(
from setuptools import setup, find_packages

# Import ourselves for version info
import patchwork

# Frankenstein long_description: version-specific changelog note + README
v = patchwork.__version__

setup(
    name='patchwork',
    version=v,
    description='Common deploy/sysadmin operations',
    license='BSD',

    long_description="""This is an unsupported alpha release! Use with caution.

Dev install: https://github.com/fabric/patchwork/tarball/master#egg=patchwork-dev""",
    author='Jeff Forcier',
    author_email='jeff@bitprophet.org',
    url='http://patchwork.fabfile.org',

    install_requires=["fabric>=1.4"],
    packages=find_packages(),

    classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ],
)
