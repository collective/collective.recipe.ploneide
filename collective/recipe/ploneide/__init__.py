# -*- coding: utf-8 -*-
"""

    Recipe ploneide

    Generate Plone debug + sauna.reload enabled launcher script in bin/

"""
import os.path

import zc.buildout

import ConfigParser


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.buildout, self.name, self.options = buildout, name, options
        options['bin-directory'] = buildout['buildout']['bin-directory']

        if not "instance" in buildout:
            raise ValueError("Buildout missing [instance] section")

        options['eggs'] = buildout['instance']['eggs']

    def create_ploneide_conf(self):
        # from here, we will create a ploneide.conf file inside ploneide's
        # directory, in where we'll store different configuration parameters
        # needed to modify the IDE's behavior
        buildout_dir = self.buildout["buildout"]["directory"]

        instance_host = self.options.get("instance-host", None)
        
        if not instance_host:
            instance_host = self.buildout["instance"]["http-address"]
            if len(instance_host.split(':')) > 1:
                instance_host = instance_host.split(':')[0]
            else:
                instance_host = '0.0.0.0'


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

        config.set('Directories', 'buildout', buildout_dir)
        config.set('Directories', 'devel', devel_directories)

        config.set('Servers', 'instance-host', instance_host)
        config.set('Servers', 'instance-port', instance_port)
        config.set('Servers', 'ploneide-host', ploneide_host)
        config.set('Servers', 'ploneide-port', ploneide_port)
        config.set('Servers', 'debug-host', debug_host)
        config.set('Servers', 'debug-port', debug_port)

        config_file = os.path.join(buildout_dir,'ploneide.conf')
        with open(config_file, 'wb') as configfile:
            config.write(configfile)

        return config_file
        

    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here
        options = self.options

        location = self.buildout["instance"]["location"]

        zope_conf_path = os.path.join(location, "etc", "zope.conf")
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
