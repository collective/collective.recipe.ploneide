# -*- coding: utf-8 -*-
"""Recipe ploneide"""
import zc.buildout


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.buildout, self.name, self.options = buildout, name, options
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['eggs'] = buildout['instance']['eggs']

    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here
        options = self.options
        requirements, ws = self.egg.working_set(['collective.recipe.ploneide'])
        zc.buildout.easy_install.scripts(
            [(options.get('control-script', self.name),
              'collective.recipe.ploneide.debug', 'main')],
            ws, options['executable'], options['bin-directory'],
            )

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return tuple()

    def update(self):
        """Updater"""
        pass
