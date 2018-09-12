## Upgrading from CKAN 2.2 to CKAN 2.8

Some steps needed to migrate from the CKAN 2.2 installation to the CKAN 2.8 one can't be
encapsulated in the provisioning roles.  This document is a guide to what they are and how to
do them.

### Running paster commands

CKAN uses `paster` to run various maintenance commands. `paster` commands need the CKAN code and config to run properly. There are a few ways to get that:

#### The `ckan` command
The CKAN installation package puts a script at `/usr/bin/ckan` that calls `paster` with the
necessary arguments.  It can only be run as root.

#### As the `vagrant` user
If you want to run a `paster` command as a non-privileged user, you need to activate the CKAN
virtualenv and run the command from the CKAN source directory:
```bash
source /usr/lib/ckan/default/bin/activate
cd /usr/lib/ckan/default/src/ckan
```
You'll also need to point it at the config file by including `-c /etc/ckan/default/production.ini`
in the command options.

### Remove tables for removed extensions

#### `deadoralive` and `issues`
Per [PR #73](https://github.com/azavea/opendataphilly-ckan/pull/73), the tables for the
`deadoralive` and `issues` plugins should be removed.

```sql
BEGIN;

-- Table for 'deadoralive'
DROP TABLE link_checker_results;

-- Tables for 'issues'
DROP TABLE issue_category;
DROP TABLE issue_comment;
DROP TABLE issue;

COMMIT;
```

#### Tables for the `unpublished_feedback` feature in `odb_theme`

These were created by `ckanext-odp_theme` but not used, and now the feature has been removed.
```sql
BEGIN;
DROP TABLE IF EXISTS ckanext_unpublished_feedback;
DROP TABLE IF EXISTS ckanext_unpublished_comments;
COMMIT;
```

### Migrate the database

- Shut down Apache to avoid contention
  ```
  service apache2 stop
  ```
- Migrate the database
  ```
  ckan db upgrade -c /etc/ckan/default/production.ini
  ```
- Restart services
  ```
  service apache2 restart
  service jetty restart
  ckan search-index rebuild -r
  ```
