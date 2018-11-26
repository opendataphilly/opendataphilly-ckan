#!/usr/bin/env python

import argparse
import os

"""
This script produces the SQL that would be produced by `ckan datastore set-permissions`, but
without requiring `paster` or a CKAN configuration. This means it can run with only a checkout
of the CKAN repository (for the .sql template) and some parameters, which facilitates provisioning
a database machine independently of a CKAN app server.

It replaces https://github.com/ckan/ckan/blob/ckan-2.2.4/ckanext/datastore/bin/datastore_setup.py
which was removed in https://github.com/ckan/ckan/commit/748c1fb6dda03300a61188165527f4e6ca31460f
"""

# The path, within the checkout of the repo, where the template file we need to fill lives
SQL_TEMPLATE = os.path.join('ckanext', 'datastore', 'set_permissions.sql')


def identifier(s):
    """
    Return s as a quoted postgres identifier

    Copied from ckanext/datastore/backend/postgres.py
    """
    return u'"' + s.replace(u'"', u'""').replace(u'\0', '') + u'"'


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Generate SQL to set the permissions on the CKAN datastore.')

    argparser.add_argument('maindb', help="the name of the ckan database")
    argparser.add_argument('datastoredb', help="the name of the datastore database")
    argparser.add_argument('mainuser', help="username of the ckan postgres user")
    argparser.add_argument('writeuser', help="username of the datastore user that can write")
    argparser.add_argument('readuser',
                           help="username of the datastore user who has only read permissions")
    argparser.add_argument('ckan_path', help="username of the datastore user that can write")

    args = argparser.parse_args()

    # Produces the SQL necessary to set datastore permissions.
    # This is adapted from `permissions_sql` in ckanext/datastore/commands.py
    template_filename = os.path.join(args.ckan_path, SQL_TEMPLATE)
    with open(template_filename) as fp:
        template = fp.read()

    sql = template.format(
        maindb=identifier(args.maindb),
        datastoredb=identifier(args.datastoredb),
        mainuser=identifier(args.mainuser),
        writeuser=identifier(args.writeuser),
        readuser=identifier(args.readuser),
    )

    print(sql)
