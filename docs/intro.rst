First Steps
===========

In this section I will try to cover some basics to work with this module.


Installation
------------
1. Download or clone this directory (green button upper right corner on github)
2. In a terminal navigate to the folder "BCO"
3. Run:

>>> python setup.py bdist_wheel
>>> pip install dist/BCO-?.?.?-py3-none-any.whl

   The ?`s needs to be replaced by the version number.


4. Check with "pip list" or "conda list" if it worked.

Documentation
-------------

The documentation is at the moment only available on linux machines.

To create the documentation:

1. In a terminal navigate to your downloaded folder "BCO"
2. cd into "docs"
3. Run:

>>> make html

   Please ignore all the warnings which occur under "checking consistency".

4. If it worked there should be a folder "generated" with some ".rst" files in it now.
    If not, you can remove the the files in generated again with running

    >>> make clean

5. cd into "\_build/html"
6. Open "index.html" with any browser


