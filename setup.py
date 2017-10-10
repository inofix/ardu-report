"""Setup the ardu-report module.

See:
https://github.com/inofix/ardu-report

Note:
Based on the https://github.com/pypa/sampleproject/blob/master/setup.py.
Consult that for comments and description..
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ardu-report',
    version='1.0.0',
    description='Get sensor data over the serial line and send it to an URL (JSON).',
    long_description=long_description,

    url='https://github.com/inofix/ardu-report',
    author='Michael Lustenberger',
    author_email='mic@inofix.ch',

    license='GPLv3',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: GNU General Public License (GPL)',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='arduino sensor json serial',

#    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    py_modules=["ardu-report"],

    install_requires=['ardu-report-lib', 'configargparse'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
#    entry_points={
#        'console_scripts': [
#            'sample=sample:main',
#        ],
#    },
)
