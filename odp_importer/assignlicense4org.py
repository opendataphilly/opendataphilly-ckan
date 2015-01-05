
import argparse
import ckanapi

from ckan_util import check_endpoints, logger


def assign_license(ckan_api, org, license):
    """Set the license for all datasets owned by an org to the one given"""

    license_id = license['id']
    license_title = license['title']
    for dataset in ckan_api.action.organization_show(id=org)['packages']:
        package = ckan_api.action.package_show(id=dataset['id'])
        package['license_id'] = license_id
        package['license_title'] = license_title
        logger.info('Set license on %s to %s' % (package['title'],
                                                 license_title))
        ckan_api.action.package_update(**package)


def get_license(ckan_api, license_id):
    """Pick out a license dict for a given license id or title"""

    for license in ckan_api.action.license_list():
        if license['id'] == license_id or license['title'] == license_id:
            return license
    return None


def main():
    parser = argparse.ArgumentParser(description='Set a license for all '
                                                 'datasets owned by an '
                                                 'organization')
    parser.add_argument('org', metavar='ORG', help='Organization')
    parser.add_argument('license', metavar='LICENSE', help='License')
    parser.add_argument('--api-key', required=True, help='CKAN API Key')
    parser.add_argument('--ckan-root', required=True, help='Root URI of CKAN '
                                                           'Instance')
    args = parser.parse_args()
    ckan = ckanapi.RemoteCKAN(args.ckan_root, apikey=args.api_key)
    # Will raise on failure.
    check_endpoints(ckan)
    license = get_license(ckan, args.license)
    assign_license(ckan, args.org, license)


if __name__ == '__main__':
    main()
