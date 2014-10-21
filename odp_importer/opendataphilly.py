import logging
import re
from urlparse import urljoin

import ckanapi
import requests


OPEN_DATA_PHILLY_ROOT = ODP = 'http://opendataphilly.org'
ODP_RESOURCE_LIST = '/api/resources/'

logger = logging.getLogger('odp-importer')


def migrate_to_ckan(odp_resource, ckan_api):
    """Migrates an Open Data Resource into CKAN via the passed ckan_api object.

    odp_resource is a Python object constructed from the ODP API JSON response for a dataset
    """
    logger.debug('Parsing ODP resource "%s"' % odp_resource['name'])
    exists = False
    pkg_slug = ckan_slugify(odp_resource['name'])
    # Check to see if it exists
    try:
        ckan_api.action.package_show(id=pkg_slug)
        exists = True
    except ckanapi.errors.NotFound:
        pass

    if exists:
        # Log existence and bail
        logger.info('CKAN Package for %s already exists; skipping.' % odp_resource['name'])
        return

    ckan_api.action.package_create(**construct_package_dict(odp_resource))
    logger.debug('Created CKAN resource for %s' % odp_resource['name'])


def construct_package_dict(odp_resource):
    """Creates a dict suitable for creating a new CKAN Package."""
    return dict(name=ckan_slugify(odp_resource['name']),
                title=odp_resource['name'],
                maintainer_email=odp_resource['contact_email'],
                notes=odp_resource['description'],
                resources=[dict(url=url['url'],
                                name=url['label']) for url in odp_resource['urls']]
               )


def ckan_slugify(string):
    """Slugifies a string to meet CKAN's requirements: lowercase alphanumeric, _, -"""
    result = str(string).strip().lower().replace(' ', '-')
    # Assume no non-ASCII
    return re.sub('[^\w\-_]*', '', result)


def get_resources():
    """Returns a list of resources in Open Data Philly"""
    return requests.get(urljoin(ODP, ODP_RESOURCE_LIST)).json()


def get_resource_detail(path):
    """Returns the detail view for the resource at path"""
    return requests.get(urljoin(ODP, path)).json()
