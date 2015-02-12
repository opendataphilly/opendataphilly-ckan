import argparse
import csv
from ckan_util import logger, check_endpoints, ckan_slugify

import ckanapi


def get_resources_from_row(row):
    """
    Extracts resources from a CSV row dict and returns them in a list
    suitable for submission to CKAN
    """

    resources = []
    for n in range(1, 6):
        t = 'resource_{{}}_{}'.format(n)
        if t.format('name') in row and row[t.format('name')] != '':
            resources.append({
                'name': row[t.format('name')],
                'description': row[t.format('description')],
                'url': row[t.format('url')],
                'format': row[t.format('format')]
            })
    return resources


def get_dataset_from_row(row):
    """
    For a CSV row dict, returns a dict that can be submitted to CKAN
    """

    dataset = {'name': ckan_slugify(row['title']),
               'title': row['title'],
               'author': row['author'],
               'author_email': row['author_email'],
               'maintainer': row['maintainer_email'],
               'license_id': row['license'],
               'notes': row['description'],
               'owner_org': row['organization'],
               'resources': get_resources_from_row(row),
               }
    if row['published'].lower() == 'false':
        dataset['extras'] = [{'key': 'published',
                              'value': 'false'}]
    if row['tags'] != '':
        dataset['tags'] = map(lambda tag: {'name': tag.strip()},
                              row['tags'].split(','))
    return dataset


def import_resources(ckan_api, row):
    """For a given csv row dict, create a CKAN package"""

    dataset = get_dataset_from_row(row)
    logger.info('Adding {}'.format(dataset['title']))
    ckan_api.action.package_create(**dataset)


def main():
    parser = argparse.ArgumentParser(description='Load datasets from OpenDataPhilly to CKAN')
    parser.add_argument('--api-key', required=True, help='CKAN API Key')
    parser.add_argument('--ckan-root', required=True, help='Root URI of CKAN Instance')
    parser.add_argument('csv', metavar='CSVFILE', type=str,
                        help='CSV filename')
    args = parser.parse_args()
    ckan = ckanapi.RemoteCKAN(args.ckan_root, apikey=args.api_key)
    check_endpoints(ckan)
    # Will raise on failure.
    with open(args.csv, 'r') as csvfile:
        for row in csv.DictReader(csvfile):
            import_resources(ckan, row)


if __name__ == '__main__':
    main()
