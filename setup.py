from setuptools import setup, find_packages
from codecs import open
from os import path
import os
import re

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Setting the version:
version_path = list(os.path.split(here))
version_path.append("_version.py")
VERSIONFILE = os.path.join(*version_path)
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"  # Pattern for finding the version string in the file _version.py
mo = re.search(VSRE, verstrline, re.M)
if mo:
    version_from_file = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name='BCO',
      version=version_from_file,
      description='Python Interface to the Max-Planck-Institute Barbados Cloud Observatory data.',
      author='Tobias Machnitzki',
      author_email='tobias.machnitzki@mpimet.mpg.de',
      url='https://github.com/tmachnitzki/BCO/',

      classifiers=[
              # How mature is this project? Common values are
              #   3 - Alpha
              #   4 - Beta
              #   5 - Production/Stable
              'Development Status :: 3 - Alpha',

              # Indicate who your project is intended for
              'Intended Audience :: Science/Research',
              'Topic :: Scientific/Engineering :: Atmospheric Science',

              # Specify the Python versions you support here. In particular, ensure
              # that you indicate whether you support Python 2, Python 3 or both.
              'Programming Language :: Python :: 2',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3.6',

              'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      ],

      # You can just specify the packages manually here if your project is
      # simple. Or you can use find_packages().
      packages=find_packages(exclude=['contrib', 'docs', 'tests', 'build']),

      # List run-time dependencies here.  These will be installed by pip when
      # your project is installed. For an analysis of "install_requires" vs pip's
      # requirements files see:
      # https://packaging.python.org/en/latest/requirements.html
      install_requires=[
          'numpy>=1.6',
          'matplotlib>=1.4',
          'future>=0.15.0',
          'scipy>=0.19.1',
          'netCDF4>=1.1.1',
          'configparser>3',
          'pytz'
      ],

      include_package_data=True,

      project_urls={
          'Documentation': 'http://bcoweb.mpimet.mpg.de/systems/BCO_python_doc/index.html',
          'BCO Blog': 'https://barbados.mpimet.mpg.de/',
          'Development': 'https://github.com/tmachnitzki/BCO'
      }
      )
