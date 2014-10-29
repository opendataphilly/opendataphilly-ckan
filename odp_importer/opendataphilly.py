import logging
from urlparse import urljoin

import requests

import ckan_util

ODP_RESOURCE_LIST = '/api/resources/'

logger = logging.getLogger('odp-importer')


class ODPToCKANImporter(object):
    """An importer class to handle moving data from OpenDataPhilly to a CKAN instance.

    :param ckan_api: A ckanapi.RemoteCKAN object
    :param odp_root: The root URI of OpenDataPhilly
    """
    class VOCABULARIES:
        NAMES = ['updates', 'data-types', 'projections']
        updates = 'updates'
        data_types = 'data-types'
        projections = 'projections'

    def __init__(self, ckan_api, odp_root):
        self.ckan_api = ckan_api
        self.odp_root = odp_root
        self.created_vocabularies = False

    def migrate_to_ckan(self, odp_resource):
        """Migrates an Open Data Resource into CKAN via the passed ckan_api object.

        :param odp_resource: Python object constructed from the ODP API JSON response for a dataset
        """
        logger.debug('Parsing ODP resource "%s"' % odp_resource['name'])
        resource_links = dict()

        pkg_slug = ckan_util.slugify(odp_resource['name'])
        # Bail if package already exists
        if ckan_util.package_exists(self.ckan_api, pkg_slug):
            logger.info('CKAN Package for %s already exists; skipping.' % odp_resource['name'])
            return

        # We create tags from update frequency, data types, and coordinates
        resource_links['tags'] = self.create_package_tags(odp_resource)

        resource_links['extras'] = self.construct_extras_list(odp_resource)

        # Groups are created from ODP tags because they are roughly the same
        # concept. CKAN groups are used for curating content; a dataset can
        # belong to multiple groups. CKAN tags, by contrast, are used for
        # adding metadata to datasets in a structured way using taxonomies. For
        # example, a CKAN tag might store information about update frequency.
        resource_links['groups'] = self.create_groups_from_tags(odp_resource['tags'])

        # Check for the organization and division; organizations can't nest, but
        # users can belong to multiple organizations, so we make organizations at
        # the lowest level available.
        org_slug = ckan_util.slugify(odp_resource['division']) or ckan_util.slugify(odp_resource['organization'])
        org_title = odp_resource['division'] or odp_resource['organization']
        if not ckan_util.organization_exists(self.ckan_api, org_slug):
            self.ckan_api.action.organization_create(name=org_slug,
                                                     title=org_title)
        resource_links['owner_org_id'] = org_slug

        self.ckan_api.action.package_create(**self.construct_package_dict(odp_resource, resource_links))
        logger.debug('Created CKAN resource for %s' % odp_resource['name'])

    def construct_package_dict(self, odp_resource, resource_links):
        """Creates a dict suitable for creating a new CKAN Package.

        :param odp_resource: Dict constructed from the ODP API JSON response
        :param resource_links: Dict of IDs of CKAN objects to which this resource has links
                                (e.g. organizations)
        """
        return dict(name=ckan_util.slugify(odp_resource['name']),
                    title=odp_resource['name'],
                    maintainer_email=odp_resource['contact_email'],
                    notes=odp_resource['description'],
                    resources=[dict(url=url['url'],
                                    name=url['label']) for url in odp_resource['urls']],
                    tags=[dict(name=tag) for tag in resource_links['tags']],
                    extras=resource_links['extras'],
                    groups=[dict(name=group) for group in resource_links['groups']],
                    owner_org=resource_links['owner_org_id'])

    def construct_extras_list(self, odp_resource):
        """Construct a list of dicts that can be passed in as the extras parameter to the CKAN API

        This is where all the OpenDataPhilly data that doesn't have an exact CKAN analogue goes.

        :param odp_resource: Dict constructed from the ODP API JSON response
        :returns: List of dicts with values {'key': xxxx, 'value': yyyy}
        """
        extras = []
        # (ODP API Key, Human-readable name in CKAN)
        extra_fields_list = [('metadata_notes', 'Metadata Notes'),
                             ('update_frequency', 'Update Frequency'),
                             ('usage', 'Usage'),
                             ('contact_phone', 'Maintainer Phone'),
                             ('data_formats', 'Data Formats'),
                             ('area_of_interest', 'Area of Interest'),
                             ('contact_url', 'Maintainer Link'),
                             ('time_period', 'Time Period'),
                             ('metadata_contact', 'Metadata Contact'),
                             ('rating', 'OpenDataPhilly Rating')]
        for field in extra_fields_list:
            if odp_resource[field[0]]:
                extras.append(dict(key=field[1], value=str(odp_resource[field[0]])))

        return extras

    def create_groups_from_tags(self, odp_tags):
        """Constructs CKAN groups from ODP tags, if necessary.

        :param odp_tags: A list of 'tag' dicts for a dataset as returned by the ODP API
        :returns: A list of dicts containing information on the newly created groups
        """
        results = []
        for tag in odp_tags:
            # Despite having different API calls, organizations and groups
            # share the same pool of slugs; add a -group suffix to prevent
            # collisions (unless some things have very odd names).
            group_slug = ckan_util.slugify(tag['name']) + '-group'
            if not ckan_util.group_exists(self.ckan_api, group_slug):
                self.ckan_api.action.group_create(name=group_slug, title=tag['name'])
            results.append(group_slug)
        return results

    def create_package_tags(self, odp_resource):
        """ODP resources have fields that are best expressed as CKAN tags, namely:
            - updates
            - formats
            - projections
        This creates tags for the package contained in odp_resource, creating the necessary
        vocabularies if needed.
        """
        # The vocabularies are pre-defined; create if needed.
        if not self.created_vocabularies:
            for vocab in self.VOCABULARIES.NAMES:
                if not ckan_util.vocabulary_exists(self.ckan_api, vocab):
                    self.ckan_api.action.vocabulary_create(name=vocab)
            self.created_vocabularies = True

        package_tags = []
        if odp_resource['updates']:
            package_tags.extend(self.upsert_tags_to_vocab(self.VOCABULARIES.updates,
                                                          [odp_resource['updates']],
                                                          slug_transform=lambda s: 'updates-%s' % s))
        package_tags.extend(self.upsert_tags_to_vocab(self.VOCABULARIES.data_types,
                                                      odp_resource['data_types'],
                                                      slug_transform=lambda s: 'format-%s' % s))
        package_tags.extend(self.upsert_tags_to_vocab(self.VOCABULARIES.projections,
                                                      [str(sys['EPSG_code']) for sys in odp_resource['coord_sys']],
                                                      slug_transform=lambda s: 'epsg-%s' % s))
        return package_tags

    def upsert_tags_to_vocab(self, vocabulary, tags, slug_transform=lambda s: s):
        """Adds tags to vocabulary if they don't already exist.

        :param vocabulary: The name of the vocabulary tags should be added to.
        :param tags: An array of names of tags to be added to the vocabulary if they don't exist
        :param slug_transform: A function which alters the slug before the tag is created
        :returns: An array of tag names which were successfully upserted
        """
        vocab_obj = self.ckan_api.action.vocabulary_show(id=vocabulary)
        processed_tags = []
        for tag in tags:
            if not tag:
                continue
            tag_slug = slug_transform(ckan_util.slugify(tag))
            if not ckan_util.tag_exists(self.ckan_api, tag_slug):
                self.ckan_api.action.tag_create(name=tag_slug,
                                                display_name=tag,
                                                vocabulary_id=vocab_obj['id'])
            processed_tags.append(tag_slug)
        return processed_tags

    def get_resources(self):
        """Returns a list of resources in Open Data Philly"""
        return requests.get(urljoin(self.odp_root, ODP_RESOURCE_LIST)).json()

    def get_resource_detail(self, path):
        """Returns the detail view for the resource at path"""
        return requests.get(urljoin(self.odp_root, path)).json()
