
import argparse
import ckanapi

from ckan_util import check_endpoints


def delete_tag(ckan_api, tag):
    """Deletes the tag given"""

    ckan_api.action.tag_delete(id=tag)


def main():
    parser = argparse.ArgumentParser(description='Deletes the tag given')
    parser.add_argument('tag', metavar='TAG', help='The tag to delete')
    parser.add_argument('--api-key', required=True, help='CKAN API Key')
    parser.add_argument('--ckan-root', required=True, help='Root URI of CKAN '
                                                           'Instance')
    args = parser.parse_args()
    ckan = ckanapi.RemoteCKAN(args.ckan_root, apikey=args.api_key)
    # Will raise on failure.
    check_endpoints(ckan)
    delete_tag(ckan, args.tag)


if __name__ == '__main__':
    main()
