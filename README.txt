.. contents::

Introduction
============

A buildout recipe to install collective.ploneide


Installing
==========

There's a buildout for your convenience in http://svn.plone.org/svn/collective/collective.ploneide/buildout that has everything needed to have PloneIDE installed.

Buildout
--------
If you're using buildout, the following steps should be enough:

 1. Create a new "ploneide" section with

    [ploneide]
    recipe = collective.recipe.ploneide

 4. Re-run buildout 

Eventually, this process will be replaced to using just the recipe. 


.. Note to recipe author!
   ---------------------
   Update the following URLs to point to your:
   
   - code repository
   - bug tracker 
   - questions/comments feedback mail 

- Code repository: http://svn.plone.org/svn/collective/collective.recipe.ploneide/
- Report bugs at http://code.google.com/p/ploneide/issues/detail?id=2
- Questions and comments to somemailing_list
