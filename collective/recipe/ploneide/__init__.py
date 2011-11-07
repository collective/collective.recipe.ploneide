# -*- coding: utf-8 -*-
"""

    Recipe ploneide

    Generate Plone debug + sauna.reload enabled launcher script in bin/

"""
import os.path

import zc.buildout


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.buildout, self.name, self.options = buildout, name, options
        options['bin-directory'] = buildout['buildout']['bin-directory']

        if not "instance" in buildout:
            raise ValueError("Buildout missing [instance] section")

        options['eggs'] = buildout['instance']['eggs']


    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here
        options = self.options

        location = self.buildout["instance"]["location"]

        zope_conf_path = os.path.join(location, "etc", "zope.conf")

        requirements, ws = self.egg.working_set(['collective.recipe.ploneide'])
        zc.buildout.easy_install.scripts(
            [(options.get('control-script', self.name),
              'collective.recipe.ploneide.debug', 'main')],
            ws, options['executable'], options['bin-directory'],
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % zope_conf_path
                         ),
            )

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return tuple()

    def update(self):
        """Updater"""
        pass
