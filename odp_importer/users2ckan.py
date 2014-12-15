from ckan_util import check_endpoints, logger

import argparse
import json
import ckanapi


def generate_password():
    """Generate a random password for a new user"""
    return 'password'  # TODO: actually generate a password


def import_users(ckan_api):
    """Get all users from users.json and try to insert them into CKAN."""

    with open('users.json', 'r') as f:
        data = json.load(f)

    for user in data['users'].values():
        fullname = user['first_name']
        password = generate_password()
        if len(user['last_name']) > 0:
            fullname += ' ' + user['last_name']
        u = {'name': user['username'],
             'email': user['email'],
             'password': password,
             'fullname': fullname,
             'state': 'active',
             'sysadmin': user['is_staff']}
        try:
            new_user = ckan_api.action.user_create(**u)
            logger.info("created user {}".format(new_user['name']))
        except Exception:  # try updating
            try:
                u['id'] = u['name']
                del u['name']
                updated_user = ckan_api.action.user_update(**u)
                logger.info('updated user {}'.format(updated_user['name']))
            except Exception as e:
                logger.error('error with user {}'.format(u['id']))


def associate_users_with_orgs(ckan_api):
    """Get all users from users.json and try to insert them into CKAN."""

    with open('users.json', 'r') as f:
        data = json.load(f)

    for groupname, group in data['organizations'].iteritems():
        for member in group:
            try:
                ckan_api.action.organization_member_create(id=groupname,
                                                           username=member,
                                                           role="admin")
                logger.info('associated {} with {}'.format(member, groupname))
            except Exception:
                logger.error('error associating {} with {}'.format(member,
                                                                   groupname))


def main():
    parser = argparse.ArgumentParser(description='Load users.json to CKAN')
    parser.add_argument('--api-key', required=True, help='CKAN API Key')
    parser.add_argument('--ckan-root', required=True, help='Root URI of CKAN Instance')
    args = parser.parse_args()
    ckan = ckanapi.RemoteCKAN(args.ckan_root, apikey=args.api_key)
    # Will raise on failure.
    check_endpoints(ckan)
    import_users(ckan)
    associate_users_with_orgs(ckan)


if __name__ == '__main__':
    main()
