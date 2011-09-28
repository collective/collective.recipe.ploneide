import os.path

from collective.ploneide.ide_server import httpd
from collective.ploneide.debug import debugger


def start(debugger, statement):
    # Let's start our auxiliar http server
    httpd.start()
    if httpd.isAlive():
        while (debugger.should_run):
            debugger.run(statement)

    # We are now quitting, let's shutdown our auxiliar server
    httpd.shutdown()


def main(args=None):
    idelpath = os.path.join(os.path.dirname(__file__), "idelauncher.py")
    statement = ('execfile( "%s")' % (idelpath,))
    start(debugger, statement)
