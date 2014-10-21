import argparse
import logging
import sys

import ckanapi

import opendataphilly


logger = logging.getLogger('odp-importer')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def check_endpoints(ckan_api):
    """Verify that the CKAN API endpoint exists and the API key is valid for it."""
    ckan_api.action.dashboard_activity_list()
    logger.debug('Successfully verified CKAN credentials')


def import_resources(ckan_api):
    """Get all data sets from Open Data Philly and try to insert them into CKAN."""
    resources = opendataphilly.get_resources()
    logger.debug('Retrieved %d resources from Open Data Philly' % len(resources))
    for resource in resources:
        detail = opendataphilly.get_resource_detail(resource['url'])
        opendataphilly.migrate_to_ckan(detail, ckan_api)

    logger.info('Successfully imported all datasets.')


def clear_resources(ckan_api):
    """Get all data sets from Open Data Philly and delete the corresponding packages from CKAN."""
    resources = opendataphilly.get_resources()
    for resource in resources:
        try:
            ckan_api.action.package_delete(id=opendataphilly.ckan_slugify(resource['name']))
        except ckanapi.errors.NotFound:
            pass
    logger.warn('Successfully deleted all datasets.\nHowever, you will need to '
                'navigate to http://your-ckan-instance/ckan-admin/trash/ and manually '
                'purge the datasets before creating new datasets with the same names.')


def main():
    parser = argparse.ArgumentParser(description='Load datasets from OpenDataPhilly to CKAN')
    parser.add_argument('--api-key', required=True, help='CKAN API Key')
    parser.add_argument('--ckan-root', required=True, help='Root URI of CKAN Instance')
    parser.add_argument('--erase', help='For each ODP resource, mark corresponding CKAN package "deleted"',
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
