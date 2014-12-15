import sys
import logging
import ckanapi
from slugify import slugify

logger = logging.getLogger('odp-importer')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def check_endpoints(ckan_api):
    """Verify that the CKAN API endpoint exists and the API key is valid for it."""

    ckan_api.action.dashboard_activity_list()
    logger.debug('Successfully verified CKAN credentials')


def package_exists(ckan_api, id):
    """Checks to see if a CKAN package identified by id exists

    :param ckan_api: A ckanapi.RemoteCKAN object
    :param id: The id / name of the package
    :rtype: bool
    """
    return ckan_resource_exists(ckan_api.action.package_show, id)


def organization_exists(ckan_api, id):
    """Same as package_exists, but for organizations"""
    return ckan_resource_exists(ckan_api.action.organization_show, id)


def group_exists(ckan_api, id):
    """Same as package_exists, but for groups"""
    return ckan_resource_exists(ckan_api.action.group_show, id)


def vocabulary_exists(ckan_api, id):
    """Same as package_exists, but for vocabularies"""
    return ckan_resource_exists(ckan_api.action.vocabulary_show, id)


def tag_exists(ckan_api, id):
    """Same as package exists but for tags"""
    return ckan_resource_exists(ckan_api.action.tag_show, id)


def ckan_resource_exists(get_func, id):
    """Executes get_func with the specified ID and checks for object existence

    :param get_func: A ckanapi getter function
    :param id: The id of the object to be gotten by get_func
    :rtype: bool
    """
    exists = False
    try:
        get_func(id=id)
        exists = True
    except ckanapi.errors.NotFound:
        pass

    return exists


def ckan_slugify(string):
    """Slugifies a string to meet CKAN's requirements: lowercase alphanumeric, _, -"""
    return slugify(unicode(string).strip())
