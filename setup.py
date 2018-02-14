from distutils.core import setup

setup(name='BCO',
      version='0.0.1',
      description='Python Interface to the Max-Planck-Institut Barbados Cloud Observatory data.',
      author='Tobias Machnitzki',
      author_email='tobias.machnitzki@mpimet.mpg.de',
      url='https://github.com/darklefknight/BCO/',
      packages=['BCO'],
      dependencies=['numpy', 'matplotlib', 'netcdf4']
     )