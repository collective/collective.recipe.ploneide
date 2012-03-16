collective.recipe.ploneide
==========================

This recipe will install and configure PloneIDE.

The recipe supports the following options:

instance-host
    Specify the host used by the Plone instance. Defaults to the host 'instance' uses.

instance-port
    Specify the port used by the Plone instance. Defaults to the port 'instance' uses.

ploneide-host
    Specify the host used by the PloneIDE itself. Defaults to be the same as ``instance-host``

ploneide-port
    Specify the port that PloneIDE should use. Defaults to the same port used by 'instance' plus 100 (If 'instance' runs in 8080, PloneIDE would run in 8180)

debug-host
    Specify the host the debugger should use. Defaults to be the same as ``ploneide-host``

debug-port
    Specify the port the debugger should use. Defaults to the same port as defined in ``ploneide-port`` plus 1 (If PloneIDE's port is 8180, then the debugger will be 8181)

directories
    Specify a list of directories to be used for development. Syntax is 'name /full/path/to/directory'. Defaults to 'src {buildout:directory}/src'

dev-manual
    Specify if the collective.developermanual should be used from its URL, or if it should be downloaded and installed localy. Valid values are "local" and "remote". Defaults to "local"

dev-manual-location
    In case ``dev-manual`` is set to "local", this option specifies the directory where it should be cloned. This is a full path directory. Defaults to "{buildout:directory}/developermanual".



Example usage
=============

.. Note to recipe author!
   ----------------------
   zc.buildout provides a nice testing environment which makes it
   relatively easy to write doctests that both demonstrate the use of
   the recipe and test it.
   You can find examples of recipe doctests from the PyPI, e.g.

     http://pypi.python.org/pypi/zc.recipe.egg

   The PyPI page for zc.buildout contains documentation about the test
   environment.

     http://pypi.python.org/pypi/zc.buildout#testing-support

   Below is a skeleton doctest that you can start with when building
   your own tests.

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = ploneide
    ...
    ... [ploneide]
    ... recipe = collective.recipe.ploneide
    ... option1 = %(foo)s
    ... option2 = %(bar)s
    ... """ % { 'foo' : 'value1', 'bar' : 'value2'})

Running the buildout gives us::

    >>> print 'start', system(buildout)
    start...
    Installing ploneide.
    Unused options for ploneide: 'option2' 'option1'.
    <BLANKLINE>


