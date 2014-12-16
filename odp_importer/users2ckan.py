
from random import SystemRandom
import argparse
import json
import ckanapi

from ckan_util import check_endpoints, logger

random = SystemRandom()

sql_reset_key = '''UPDATE "user" SET "reset_key" = '%s' WHERE "id" = '%s';\n'''

reset_url = 'http://localhost:8025/user/reset/%s?key=%s'


def generate_password():
    """Generate a random password for a new user"""

    chars = '23456789qwertyuiopasdfghjkzxcvbnmQWERTYUPADSFGHJKLZXCVBNM$!#'
    # this long password essentially locks the account
    return ''.join([random.choice(chars) for x in range(30)])


def generate_reset_key():
    """Generate a random password for a new user"""

    chars = '1234567890abcdef'
    return ''.join([random.choice(chars) for x in range(10)])


def write_info(username, email, id, reset_key, csv, sql):
    csv.write('%s,%s,%s\n' % (username, email,
                              reset_url % (id, reset_key)))
    sql.write(sql_reset_key % (reset_key, id))


def import_users(ckan_api):
    """Get all users from users.json and try to insert them into CKAN."""

    with open('users.json', 'r') as f:
        data = json.load(f)

    csv = open('created_accounts.csv', 'w')
    sql = open('assign_reset_key.sql', 'w')

    for user in data['users'].values():
        fullname = user['first_name']
        if len(user['last_name']) > 0:
            fullname += ' ' + user['last_name']
        reset_key = generate_reset_key()
        u = {'name': user['username'],
             'email': user['email'],
             'password': generate_password(),  # password is required
             'fullname': fullname,
             'state': 'active',
             'sysadmin': user['is_staff']}
        try:
            updated_user = ckan_api.action.user_create(**u)
            write_info(user['username'], user['email'], updated_user['id'],
                       reset_key, csv, sql)
            logger.info("created user %s" % updated_user['name'])
        except Exception:  # try updating
            try:
                u['id'] = u['name']
                del u['name']
                updated_user = ckan_api.action.user_update(**u)
                write_info(user['username'], user['email'], updated_user['id'],
                           reset_key, csv, sql)
                logger.info('updated user %s' % updated_user['name'])
            except Exception:
                logger.error('error with user %s' % u['id'])

    f.close()


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
                logger.info('associated %s with %s' % (member, groupname))
            except Exception:
                logger.error('error associating %s with %s' % (member,
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
