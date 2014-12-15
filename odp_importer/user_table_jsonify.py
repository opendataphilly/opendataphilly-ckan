#!/usr/bin/env python
'''
Given an OpenDataPhilly .sql file as an arguement, this script will write
a json file with users and groups they would likely be associated with
to users.json. This file can be double checked and modified before being
committed to a CKAN instance.

'''


import json
import sys
from ckan_util import ckan_slugify as slugify

fake_email = True


def gen_fake_email(user):
    return '{}@fakedomain.fake'.format(user['username'])


def str_to_bool(x):
    if x.startswith('t'):
        return True
    return False

user_indicies = [
    ('id', 0, int),
    ('username', 1, str),
    ('first_name', 2, str),
    ('last_name', 3, str),
    ('email', 4, str),
    ('is_staff', 6, str_to_bool),
    ('is_active', 7, str_to_bool),
    ('is_superuser', 8, str_to_bool),
    ('last_login', 9, str),
    ('date_joined', 10, str)
]

resource_indicies = [
    ('organization', 4, lambda x: x.decode('utf8')),
    ('division', 5, lambda x: x.decode('utf8')),
    ('created_by_id', 16, int),
    ('modified_by_id', 17, int)
]

users = {}
orgs = {}

rejectlist_domains = [
    'goood-mail.net',
    'groupd-mail.net',
    'need-mail.com',
    'wkime.pl',
    'mail.ru'
]
acceptlist_domains = [
    'azavea.com',
    'phila.gov',
    'phila.k12.pa.us'
]


def user_spam_filter(user):
    if user['email'].split('@')[-1] in acceptlist_domains:
        return True
    if user['email'].split('@')[-1] in rejectlist_domains:
        return False
    if user['last_name'] == user['first_name'] and \
            user['last_name'][-2:-1] == user['last_name'][-2:-1].upper():
        return False
    return True


def line_to_dict(line, indexmap):
    vals = line.split('\t')
    d = {}
    for k, i, t in indexmap:
        d[k] = t(vals[i])
    return d

with open(sys.argv[1], 'r') as f:
    for L in f:  # seek to users table
        if L.startswith('COPY auth_user'):
            break
    for L in f:
        L = L.rstrip('\n')
        if L == '\\.':
            break
        user = line_to_dict(L, user_indicies)
        user['username'] = user['username'].lower()
        if fake_email:
            user['email'] = gen_fake_email(user)
        if user_spam_filter(user):
            if user['is_active']:
                users[user['id']] = user
        else:
            domain = user['email'].split('@')[-1]
            if domain != 'hotmail.com':
                print domain, user['first_name'], user['last_name']

    for L in f:  # continue seeking to resource table
        if L.startswith('COPY opendata_resource'):
            break
    for L in f:
        L = L.rstrip('\n')
        if L == '\\.':
            break
        res = line_to_dict(L, resource_indicies)
        res['org_slug'] = slugify(res['division']) or \
            slugify(res['organization'])
        if res['org_slug'] not in orgs:
            orgs[res['org_slug']] = []
        userlist = set(orgs[res['org_slug']])
        try:
            userlist.add(users[res['created_by_id']]['username'])
        except KeyError:
            pass
        try:
            userlist.add(users[res['modified_by_id']]['username'])
        except KeyError:
            pass
        orgs[res['org_slug']] = list(userlist)


with open('users.json', 'w') as f:
    f.write(json.dumps({'users': users, 'organizations': orgs}, indent=2))

print "{} users".format(len(users))