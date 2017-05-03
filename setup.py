#!/usr/bin/env python
#
# Setup prog for Rubygemn RPM builder

import sys
from distutils.core import setup

release_version="0.9.0"


etc_files = ['etc/rubygemrpm.conf',
             'etc/rubygem-GEM.spec.template',
             ]

rpm_data_files=[#('/etc/autopyfactory', libexec_files),
                ('/etc/rubygemrpm', etc_files),                                      
               ]


home_data_files=[#('etc', libexec_files),
                 ('etc', etc_files),
                 ]
setup(
    name="rubygemrpm",
    version=release_version,
    description='Utility for fetching Ruby gems and generating RPMs, while recursively fetching deps',
    long_description='''Utility for fetching Ruby gems and generating RPMs, while recursively fetching deps''',
    license='GPL',
    author='John Hover',
    author_email='jhover@bnl.gov',
    url='https://www.racf.bnl.gov/experiments/usatlas/griddev/',
    modules=[ 'rubygemrpm',
              ],
    classifiers=[
          'Development Status :: 3 - Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GPL',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: System Administration :: Management',
    ],
    scripts=[ 'scripts/rubygemrpm',
             ]

)


