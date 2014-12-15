import argparse
import logging
import sys
import json
import ckanapi


logger = logging.getLogger('odp-importer')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def generate_password():
    """Generate a random password for a new user"""
    return 'password'  # TODO: actually generate a password


def check_endpoints(ckan_api):
    """Verify that the CKAN API endpoint exists and the API key is valid for it."""

    ckan_api.action.dashboard_activity_list()
    logger.debug('Successfully verified CKAN credentials')


def import_users(ckan_api):
    """Get all users from users.json and try to insert them into CKAN."""

    with open('users.json', 'r') as f:
        data = json.load(f)

    for user in data['users'].values():
        fullname = user['first_name']
        password = generate_password()
        if len(user['last_name']) > 0:
            fullname += ' ' + user['last_name']
        u = {'name': user['username'].lower(),
             'email': user['email'],
             'password': password,
             'fullname': fullname,
             'state': 'active',
             'sysadmin': user['is_staff']}
        try:
            new_user = ckan_api.action.user_create(**u)
            print "created user {}".format(new_user['name'])
        except Exception:  # try updating
            try:
                u['id'] = u['name']
                del u['name']
                updated_user = ckan_api.action.user_update(**u)
                print "updated user {}".format(updated_user['name'])
            except Exception as e:
                print "error with user {}".format(u['id'])


def main():
    parser = argparse.ArgumentParser(description='Load users.json to CKAN')
    parser.add_argument('--api-key', required=True, help='CKAN API Key')
    parser.add_argument('--ckan-root', required=True, help='Root URI of CKAN Instance')
    args = parser.parse_args()
    ckan = ckanapi.RemoteCKAN(args.ckan_root, apikey=args.api_key)
    # Will raise on failure.
    check_endpoints(ckan)
    import_users(ckan)


if __name__ == '__main__':
    main()
