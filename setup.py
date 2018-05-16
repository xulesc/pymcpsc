"""Distutils based setup script for pymcpsc.
This uses Distutils (http://python.org/sigs/distutils-sig/) the standard
python mechanism for installing packages. For the easiest installation
just type the command:
python setup.py install
For more in-depth instructions, see the README file.
"""
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Make sure we have the right Python version.
if sys.version_info[:2] < (2, 7):
    sys.stderr.write("pymcpsc requires Python 2.7, or Python 3.5 or later. "
                     "Python %d.%d detected.\n" % sys.version_info[:2])
    sys.exit(1)
elif sys.version_info[0] == 3 and sys.version_info[:2] < (3, 5):
    sys.stderr.write("pymcpsc requires Python 3.5 or later (or Python 2.7). "
                     "Python %d.%d detected.\n" % sys.version_info[:2])
    sys.exit(1)

if sys.version_info < (3, 0):
    install_requires = ['numpy>=1.9',
                        'pandas>=0.17',
                        'scikit-learn>=0.16',
                        'matplotlib>=1.4',
                        'seaborn>=0.6',
                        'dendropy>=4.3',
                        'ete3<3.1'],
else:
    install_requires = ['numpy>=1.10',
                        'pandas>=0.18',
                        'scikit-learn>=0.17',
                        'matplotlib>=1.5',
                        'seaborn>=0.8',
                        'ete3<3.1',
                        'dendropy'],

config = {
    'description':
        'a utility for large-scape multi-criteria protein structure comparison',
    'author': 'Anuj Sharma',
    'url': 'xxxx',
    'download_url': 'xxxx',
    'author_email': 'asharma@di.uoa.gr',
    'version': '0.1',
    'install_requires': install_requires,
    'packages': ['pymcpsc'],
    'zip_safe': False,  # expand egg
    'include_package_data': True,
      # causes includes to be resolved from MANIFEST.in
    'scripts': [],
    'name': 'pymcpsc',
    'entry_points': {
        'console_scripts': [
              'run-pymcpsc = pymcpsc.run_pymcpsc:main'
        ]
    }
}

setup(**config)
