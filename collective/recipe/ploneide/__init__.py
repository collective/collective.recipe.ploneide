# -*- coding: utf-8 -*-
"""

    Recipe ploneide

    Generate Plone debug + sauna.reload enabled launcher script in bin/

"""
import os.path

import zc.buildout

import ConfigParser

import sys
import os
import subprocess

from zc.recipe.egg import Egg

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.egg = Egg(buildout, options['recipe'], options)
        self.buildout, self.name, self.options = buildout, name, options
        options['bin-directory'] = buildout['buildout']['bin-directory']

        if not "instance" in buildout:
            raise ValueError("Buildout missing [instance] section")

        options['eggs'] = buildout['instance']['eggs']

    def install_developer_manual(self):
        # First try to pull existing developermanual wc
        print "About to start installing the collective.developermanual"

        git_url = "git://github.com/collective/collective.developermanual.git"
        location = self.options.get("dev-manual-location", None)
        cwd = os.getcwd()
        buildout_dir = self.buildout["buildout"]["directory"]
        os.chdir(buildout_dir)

        if not location:
            location = os.path.join(buildout_dir, "developermanual")

        if os.path.exists(location):
            os.chdir(location)
            exists = True
        else:
            parent = os.path.dirname(location)
            if not os.path.exists(parent):
                try:
                    os.makedirs(parent)
                except OSError:
                    print "You might not have permission to create %s" % parent
                    sys.exit(1)

            exists = False

        kwargs = {}
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE

        if exists:
            # developermanual was already cloned, need to pull
            print ("We seem to have an existing manual in %s, let's try to "
                   "update it" % os.getcwd())
            cmd = ['git','pull','--quiet']
            res = subprocess.Popen(cmd, **kwargs)
            stdout, stderr = res.communicate()
            if stdout or stderr:
                # This doesn't seem to be a git repo. Let's remove it
                # and try to clone it
                print "This was not a valid directory, removing..."
                exists = False
                os.chdir(buildout_dir)
                os.rmdir(location)
            else:
                print "Manual updated successfuly"

        if not exists:
            print "We need to do a fresh checkout, this might take a while..."
            os.chdir(parent)
            dirname = os.path.basename(location)
            cmd = ['git','clone', "--quiet", git_url, dirname]
            res = subprocess.Popen(cmd, **kwargs)
            stdout, stderr = res.communicate()
            if stdout or stderr:
                print ("Something went wrong, please check the error and "
                       "try again.")
                print stdout
                print stderr
                sys.exit(1)

            else:
                os.chdir(location)
                print "Done. Manual located in %s" % os.getcwd()

        print "Bootstrapping..."
        cmd = ['python', 'bootstrap.py']
        res = subprocess.Popen(cmd, **kwargs)
        stdout, stderr = res.communicate()

        print "Running buildout. This might take a while..."
        cmd = ['./bin/buildout']
        res = subprocess.Popen(cmd, **kwargs)
        stdout, stderr = res.communicate()

        print "Generating doc. This might take a while..."
        cmd = ['make', 'html']
        res = subprocess.Popen(cmd, **kwargs)
        stdout, stderr = res.communicate()

        self.developer_manual_uri = os.path.join(location, 'build/html')

        os.chdir(cwd)

        print "All Done."

    def create_ploneide_conf(self):
        # from here, we will create a ploneide.conf file inside ploneide's
        # directory, in where we'll store different configuration parameters
        # needed to modify the IDE's behavior
        buildout_dir = self.buildout["buildout"]["directory"]
        location = self.buildout["instance"]["location"]

        zope_conf_path = os.path.join(location, "etc", "zope.conf")

        instance_host = self.options.get("instance-host", None)

        if not instance_host:
            instance_host = self.buildout["instance"]["http-address"]
            if len(instance_host.split(':')) > 1:
                instance_host = instance_host.split(':')[0]
            else:
                instance_host = 'localhost'


        instance_port = self.options.get("instance-port", None)

        if not instance_port:
            instance_port = self.buildout["instance"]["http-address"]
            if len(instance_port.split(':')) > 1:
                instance_port = instance_port.split(':')[1]

        instance_port = int(instance_port)

        ploneide_host = self.options.get("ploneide-host", instance_host)
        ploneide_port = int(self.options.get("ploneide-port", None) or
                            instance_port + 100)

        debug_host = self.options.get("debug-host", ploneide_host)
        debug_port = int(self.options.get("debug-port", None) or
                            ploneide_port + 1)

        dirs = self.options.get("directories", None)
        if dirs:
            devel_directories = dict([i.split(' ') for i in dirs.split('\n')
                                      if i!= ''])
        else:
            devel_directories = {'src': os.path.join(buildout_dir,'src')}

        config = ConfigParser.RawConfigParser()

        config.add_section('Directories')
        config.add_section('Servers')
        config.add_section('Dev Manual')

        config.set('Directories', 'buildout', buildout_dir)
        config.set('Directories', 'devel', devel_directories)
        config.set('Directories', 'zope-conf-file', zope_conf_path)

        config.set('Servers', 'instance-host', instance_host)
        config.set('Servers', 'instance-port', instance_port)
        config.set('Servers', 'ploneide-host', ploneide_host)
        config.set('Servers', 'ploneide-port', ploneide_port)
        config.set('Servers', 'debug-host', debug_host)
        config.set('Servers', 'debug-port', debug_port)

        config.set('Dev Manual', 'location', self.developer_manual_uri)

        config_file = os.path.join(buildout_dir,'ploneide.conf')
        with open(config_file, 'wb') as configfile:
            config.write(configfile)

        return config_file


    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here
        options = self.options

        self.developer_manual_uri = ""

        install_dev_manual = self.options.get("dev-manual", "local")

        if install_dev_manual == "local":
            self.install_developer_manual()
        else:
            print "Using online collective.developermanual"
            self.developer_manual_uri = "http://developer.plone.org"

        config_file = self.create_ploneide_conf()

        requirements, ws = self.egg.working_set(['collective.recipe.ploneide'])
        zc.buildout.easy_install.scripts(
            [(options.get('control-script', self.name),
              'collective.ploneide.ploneide.main', 'main')],
            ws, options['executable'], options['bin-directory'],
            arguments = ('\n        %r' % config_file),
            )

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return tuple()

    def update(self):
        """Updater"""
        pass
