# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, with_statement

import random
import string

from revolver.core import sudo
from revolver import command, package, file, service
from revolver import contextmanager as ctx
from revolver import directory as dir


def _preseed_server(root_password):
    seed_config = """# Mysql preseed generated by revolver
mysql-server mysql-server/root_password password %(root_password)s
mysql-server mysql-server/root_password_again password %(root_password)s
mysql-server mysql-server/start_on_boot boolean true
""" % {"root_password": root_password}
    seed_dir = "/var/cache/local/preseeding/"
    seed_file = seed_dir + "mysql-server.seed"

    if file.exists(seed_file):
        return

    with ctx.sudo():
        dir.create(seed_dir, recursive=True)
        file.write(seed_file, seed_config)
        sudo("debconf-set-selections %s" % seed_file)


def _store_root_cnf(password):
    cnf_config = """# Config generated by revolver
[client]
host = localhost
user = root
password = %s
""" % password
    cnf_dir = "/etc/mysql/"
    cnf_file = cnf_dir + "root.cnf"

    if file.exists(cnf_file):
        return

    with ctx.sudo():
        file.write(cnf_file, cnf_config)
        file.link(cnf_file, "/root/.my.cnf")


def _generate_password(length=15):
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for x in xrange(length))


def _execute_mysql(sql):
    sudo("mysql --defaults-file=/etc/mysql/root.cnf -e '%s'" % sql)


def install(server=False, password=None):
    packages = ["mysql-client", "libmysqlclient-dev"]

    if server:
        if not password:
            password = _generate_password()

        _preseed_server(password)
        _store_root_cnf(password)
        packages.append("mysql-server")

    # TODO Use this always on package.install?
    with ctx.prefix("export DEBIAN_FRONTEND=noninteractive"):
        package.install(packages)

    if server:
        service.start("mysql")


def ensure(server=False, password=None):
    commands_found = True

    if not command.exists("mysql"):
        commands_found = False

    if server and not command.exists("mysqld"):
        commands_found = False

    if commands_found:
        return

    install(server=server, password=password)


def ensure_database(name, charset=None, collate=None):
    sql = "CREATE DATABASE IF NOT EXISTS `%s`" % name

    if charset:
        sql += " DEFAULT CHARACTER SET %s" % charset

    if collate:
        sql += " DEFAULT COLLATE %s" % collate

    _execute_mysql(sql)
