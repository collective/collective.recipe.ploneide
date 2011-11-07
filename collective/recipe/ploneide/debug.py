"""

    Launch Zope w/debugger interface listening and sauna.reload running.

"""
import sys
import os
import os.path

from collective.ploneide.ide_server import httpd
from collective.ploneide.debug import debugger

try:
    # This will run in monkey patches giving in the fork reload
    # support for plone
    import sauna.reload
    FROM_FINLAND_WITH_LOVE=True
except ImportError:
    print "No sauna.reload available"
    FROM_FINLAND_WITH_LOVE=False

def start(debugger, statement):
    # Let's start our auxiliar http server
    httpd.start()
    if httpd.isAlive():
        while (debugger.should_run):
            debugger.run(statement)

    # We are now quitting, let's shutdown our auxiliar server
    httpd.shutdown()

def warm_up_the_sauna():
    """
    Configure in sauna.reload auto-reloading of SRC modules.
    """

    print "Configuring module auto-reload"

    # XXX: Do not assume getcwd() is buildout root, but get in from some opts

    from sauna.reload.reloadpaths import ReloadPaths
    sauna.reload.reload_paths = ReloadPaths([os.path.join(os.getcwd(), "src")])

    from sauna.reload import autoinclude, fiveconfigure
    from sauna.reload import reload_paths
    from sauna.reload import monkeypatcher

    monkeypatcher.PATCHED = True

    if reload_paths:
        # 1) Defer autoinclude of packages found under reload paths.
        autoinclude.defer_paths()
        # 2) Prevent Five from finding packages under reload paths.
        fiveconfigure.defer_install()


def run_zope(args):
    """ Run Zope without a nested process launch.

    This enables us to have the debugger intact for the process.

    :param args:
    """
    # Start zope instance as a web server
    # Zope launcher module
    import Zope2.Startup.run

    zope_main = Zope2.Startup.run.__file__

    if zope_main.endswith(".pyc"):
        # Run as .py file
        zope_main = zope_main[:-1]

    # Tinker with command-line to emulate normal Zope launch
    sys.argv = [ zope_main, "-X", "debug-mode=on"] + args

    # Instead of spawning zopectl and Zope in another process, execute Plone in the context of this Python interpreter
    # to have pdb control over the code
    #print "Executing: %s %s" % (zope_main, sys.argv)

    if FROM_FINLAND_WITH_LOVE:
        warm_up_the_sauna()

    Zope2.Startup.run.run()

import plone.recipe.zope2instance.ctl

def main(args):
    #idelpath = os.path.join(os.path.dirname(__file__), "idelauncher.py")
    #statement = ('execfile( "%s")' % (idelpath,))
    #start(debugger, statement)
    run_zope(args)
