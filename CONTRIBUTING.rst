Contributing to Tagalog
=======================

Before contributing to Tagalog, please read the following guidance.


Hacking on the code
-------------------

You are encouraged to use pip_, virtualenv_, and virtualenvwrapper_ to aid
working with Tagalog when developing. You can make a virtualenv and install a
"development" copy of Tagalog into it by doing the following from the root of
your repository checkout, assuming you have installed and configured virtualenv
and virtualenvwrapper::

    $ mkvirtualenv tagalog
    $ pip install -e .

If this sequence of commands completes successfully you will end up with the
Tagalog tools in your ``$PATH``::

    $ echo hello | logtag
    {"@timestamp": "2013-04-08T09:44:02.738947Z", "@message": "hello"}

These commands are thin wrappers which point to your checked out source code,
and they will immediately reflect changes you make to the Tagalog code. If you
add or update the list of commands in ``setup.py`` you will need to rerun

::
    $ pip install -e .

.. _pip: http://www.pip-installer.org/
.. _virtualenv: http://www.virtualenv.org/
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/


Testing
-------

Tagalog uses Tox_ to automate testing against multiple versions of Python, and
to ensure test isolation. Install tox and run the tests using::

    $ tox

To run tests against a specific version of Python (say, 2.7) run::

    $ tox -e py27

You can also run the tests against your default virtualenv Python by running
``nosetests`` from the root of the repository (you will need to ``pip install
nose mock`` first), but please note that you should always run the isolated
tests using Tox before pushing code.

.. _Tox: http://tox.readthedocs.org/


Version numbers
---------------

Tagalog uses the `Semantic Versioning specification <http://semver.org/>` to
determine appropriate version numbers. Please familiarise yourself with its
contents before bumping the version number.

Version numbers should never be bumped on branches.


Releasing Tagalog
-----------------

You'll need to find an existing project administrator of Tagalog on PyPI to add
you as a project maintainer with permissions to release new versions. The
process of releasing a new version goes as follows:

1. Ensure that ``HEAD`` is pushed and that the latest Travis build has passed.
2. Bump the version of Tagalog in `tagalog/__init__.py`. The version bump should
   be its own commit with a message of the form "Bump version -> vX.Y.Z" 
3. Release a new source distribution::

       $ python setup.py sdist register upload
4. If the release works, tag your commit and push the tag to GitHub::

       $ git tag vX.Y.Z
       $ git push --tags
