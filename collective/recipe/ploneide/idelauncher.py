# -*- coding: utf-8 -*-
"""

    Through-the-IDE launch script for Eclipse and Plone 3.1.x.

    Assume default builtout folder layout with Omelette. Drop this script to instance/bin folder. Use instance folder as the
    working folder when running the script.

    Related tutorial: http://plone.org/documentation/how-to/developing-plone-with-eclipse-ide

    Omelette: http://theploneblog.org/blog/archive/2008/03/10/collective-recipe-omelette-for-more-navigable-eggs

    Please visit us at http://mfabrik.com
    
    Use following arguments:
    
        To start Plone server.
        
            idelauncher.py (no parameters)
            
        To run all tests in a product:
        
            test -s plone.app.contentrules 
            
        To run a specific test case:
        
            test -s plone.app.contentrules -t TestWorkflowTriggering (py modulename without extension)
            
    Zope does not give an error if the product/case is missing, but runs 0 tests.
    
    
    Version history
    ===============

    1.8: Plone 4 compatibility

    1.7: Added optional use of "debug-instance" launcher if present

    1.6: Fixed typo in UNIX instance script name
    
    1.5: Updated to Windows compatibility
    
    1.4: Added Zope debug shell compatiblity
    
    1.3: Added pydevd compatibility
    
    1.2: Fixed signal handler problems with collective.autorestart (pyinotify)
    
    1.1: Fixed unit test running problems

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__docformat__ = "epytext"
__license__ = "3-clause BSD"
__copyright__ = "2008-2010 Twinapex Research"
__version__ = "1.5"
__url__ = "http://plone.org/documentation/kb/developing-plone-with-eclipse/ide-compatible-launcher-script"

import os
import sys

# Guess our working directory based on the location of this file
module = sys.modules[__name__]
PROJECT_FOLDER=os.path.join(os.path.dirname(module.__file__), "..")

# Set up Zope environment variables
os.environ["ZOPE_HOME"]=os.path.join(PROJECT_FOLDER, "parts/zope2")
os.environ["INSTANCE_HOME"]=os.path.join(PROJECT_FOLDER, "parts/instance")
os.environ["CONFIG_FILE"]=os.path.join(PROJECT_FOLDER, "parts/instance/etc/zope.conf")
os.environ["SOFTWARE_HOME"]=os.path.join(PROJECT_FOLDER, "parts/zope2/lib/python")



# Omelette and other path completion goodies must not exist in sys.path when launching the instance.
# PyDev inserts it there for import autocompletion, but Plone
# chokes if it finds duplicate imports and other Omelette
# quirkies during start up

# python2.4 -> standard python library
# pysrc -> pydevd remote debugger support


allowed_path_marks = ["python2.4", # System Pythons 
                      "python2.5",
                      "python2.6",
                      "python2.7",                      
                      "pysrc", # PyDev IDE
                      "python\\lib", # Windows system Python                      
                      "DLL" #
                      ]

def is_good_path(path):
    for p in allowed_path_marks:
        if p in path:
            return True
    
    return False

# Make sure that Python path contains only eggs provided by the system  
sys.path = [ x for x in sys.path if is_good_path(x) ]

# Use instance script to initialize PYTHONPATH

if sys.platform == "win32":
    script = "instance-script.py"
else:
    # Also for unix try debug-instance
    for name in ["debug-instance", "instance", "xxx"]:
        path = os.path.join(PROJECT_FOLDER, "bin", name)
        if os.path.exists(path):
                script = name
                break 

    if name == "xxx":
	print "Could not guess Zope start-up script name in bin folder"
	sys.exit(1)

    # These must be updated accordingly 
    os.environ["INSTANCE_HOME"]=os.path.join(PROJECT_FOLDER, "parts/" + script)
    os.environ["CONFIG_FILE"]=os.path.join(PROJECT_FOLDER, "parts/" + script + "/etc/zope.conf")


print "Starting Zope with script " + script + " and configuration:" + str(os.environ.get("CONFIG_FILE"))

instance_script = open(os.path.join(PROJECT_FOLDER, "bin", script), "rt")
data = ""
for line in instance_script:
    if line.startswith("if __name__ =="):
        # A hack to evaluate sys.path imports from instance script
        break
    data += line + "\n"

instance_script.close()


exec(data, globals())


def fix_signal_handlers():
    """ Signal handlers + pyinotify are incompatible combination, preventing running collective.autorestart from IDE """
    from Signals import Signals
    
    def dummy_register(loggers):
        """ Monkey-patched signal registerer - do not register any signals """
        pass

    Signals.registerZopeSignals = dummy_register
      

if len(sys.argv) > 1 and sys.argv[1] in ("test", "debug"):    
    # Start Zope test runner or console mode.
    # We can invoke this using zope2instance.ctl, since its do_test()
    # does not fork a new process    
    
    old_arg = sys.argv[:]
    sys.argv = [ "ctl.py", "-C", os.environ["CONFIG_FILE"], sys.argv[1]]
    sys.argv += old_arg[2:]

    
    from plone.recipe.zope2instance import ctl
    ctl.main(sys.argv[1:])
else:    
       
    # Start zope instance as a web server
    # Zope launcher module
    ZOPE_RUN = os.path.join(os.environ["SOFTWARE_HOME"], "Zope2/Startup/run.py")
    
    
    if not os.path.exists(ZOPE_RUN):
        # Plone 4
        import Zope2.Startup.run                    
        ZOPE_RUN = Zope2.Startup.run.__file__
        if ZOPE_RUN.endswith(".pyc"):
            # Run as .py file
            ZOPE_RUN = ZOPE_RUN[:-1]

    # Tinker with command-line to emulate normal Zope launch
    sys.argv = [ ZOPE_RUN, "-C", os.environ["CONFIG_FILE"], "-X", "debug-mode=on"]


    fix_signal_handlers()

    # Instead of spawning zopectl and Zope in another process, execute Plone in the context of this Python interpreter
    # to have pdb control over the code
    execfile(ZOPE_RUN)

