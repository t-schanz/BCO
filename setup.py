from setuptools import setup, find_packages

setup(name='BCO',
      version='0.0.1',
      description='Python Interface to the Max-Planck-Institut Barbados Cloud Observatory data.',
      author='Tobias Machnitzki',
      author_email='tobias.machnitzki@mpimet.mpg.de',
      url='https://github.com/darklefknight/BCO/',

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
            'Programming Language :: Python :: 3.6',
      ],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['docs']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'matplotlib>=1.4',
        'netCDF4>=1.1.1',
        'numpy>=1.6',
      ],


     )