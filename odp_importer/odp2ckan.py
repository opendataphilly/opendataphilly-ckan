import argparse
from ckan_util import logger, check_endpoints

import ckanapi

import opendataphilly

ODP_ROOT = 'http://opendataphilly.org'


def import_resources(ckan_api):
    """Get all data sets from Open Data Philly and try to insert them into CKAN."""
    importer = opendataphilly.ODPToCKANImporter(ckan_api, ODP_ROOT)
    resources = importer.get_resources()
    logger.debug('Retrieved %d resources from Open Data Philly' % len(resources))
    for resource in resources:
        detail = importer.get_resource_detail(resource['url'])
        importer.migrate_to_ckan(detail)

    logger.info('Successfully imported all datasets.')


def clear_resources(ckan_api):
    """Attempt to delete as much as possible from the target CKAN instance."""
    logger.info("Deleting packages from CKAN instance")
    resources = ckan_api.action.package_list()
    for resource in resources:
        ckan_api.action.package_delete(id=resource)

    logger.info("Deleting organizations from CKAN instance")
    organizations = ckan_api.action.organization_list()
    for org in organizations:
        ckan_api.action.organization_purge(id=org)

    logger.info("Deleting groups from CKAN instance")
    groups = ckan_api.action.group_list()
    for group in groups:
        ckan_api.action.group_purge(id=group)

    logger.info("Deleting free tags from CKAN instance")
    tags = ckan_api.action.tag_list()
    for tag in tags:
        ckan_api.action.tag_delete(id=tag)

    logger.info("Deleting vocabulary tags from CKAN instance")
    vocabs = ckan_api.action.vocabulary_list()
    for vocab in vocabs:
        tags = ckan_api.action.tag_list(vocabulary_id=vocab['id'])
        for t in tags:
            ckan_api.action.tag_delete(id=t, vocabulary_id=vocab['id'])
        ckan_api.action.vocabulary_delete(id=vocab['id'])

    logger.warn('Successfully cleared CKAN instance.\nHowever, you will need to '
                'navigate to http://your-ckan-instance/ckan-admin/trash/ and manually '
                'purge the old datasets before creating new datasets with the same names.')


def main():
    parser = argparse.ArgumentParser(description='Load datasets from OpenDataPhilly to CKAN')
    parser.add_argument('--api-key', required=True, help='CKAN API Key')
    parser.add_argument('--ckan-root', required=True, help='Root URI of CKAN Instance')
    parser.add_argument('--erase', help='Clear all data from target CKAN instance',
                        action='store_true')
    args = parser.parse_args()
    ckan = ckanapi.RemoteCKAN(args.ckan_root, apikey=args.api_key)
    # Will raise on failure.
    check_endpoints(ckan)
    if args.erase:
        clear_resources(ckan)
    else:
        import_resources(ckan)


if __name__ == '__main__':
    main()
