# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, with_statement

from revolver.core import run
from revolver import contextmanager as ctx
from revolver import directory as dir
from revolver import package


def install():
    package.ensure("git-core")

    if not dir.exists(".rbenv"):
        run("git clone git://github.com/sstephenson/rbenv.git .rbenv")
        return

    with ctx.cd(".rbenv"):
        run("git pull")


def ensure():
    if not dir.exists(".rbenv"):
        install()
