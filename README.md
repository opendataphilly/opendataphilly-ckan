opendataphilly-ckan
===================

Port of OpenDataPhilly to CKAN

Development Dependencies
------------------

* [Vagrant](http://www.vagrantup.com)
* [Ansible](http://www.ansible.com)


Development Installation
---------------

1. Make sure you have the development dependencies installed
2. Clone the [ckanext-odp_theme](https://github.com/azavea/ckanext-odp_theme) repository to this directory's parent directory
3. Copy `deployment/ansible/group_vars/vagrant.example` to `vagrant` and edit with your disqus shortname and e-mail credentials. If e-mail credentials are left unconfigured, e-mails will not be sent out.
4. Run `vagrant up`; once the Ansible provisioner finishes, CKAN will be available at http://localhost:8025
5. Creating a sysadmin user:
```
  vagrant ssh
  . /usr/lib/ckan/default/bin/activate
  cd /usr/lib/ckan/default/src/ckan
  paster sysadmin add <USERNAME> -c /etc/ckan/default/production.ini
```

Deployment
-----------------

1. Launch a server running Ubuntu 14.04. This server should be accessible from the deployment computer over SSH, and should have HTTP and HTTPS access to the internet.
2. Copy `deployment/ansible/hosts/hosts.staging.example` to `hosts.staging` and enter the address of the server that was just launched.
3. Copy `deployment/ansible/group_vars/staging.example` to `staging` and edit any settings you wish to change (see above). Make sure that `ckan_site_url` matches the address at which you will access the site.
4. Run `ANSIBLE_HOST_KEY_CHECKING=false ansible-playbook --private-key=/absolute/path/to/server/key/file.pem --user=ubuntu --inventory-file=deployment/ansible/hosts/hosts.staging deployment/ansible/staging.yml -v`


Migrating database from host to host
-----------------

### Export the database from the source host
```
cd /usr/lib/ckan/default/src/ckan
/usr/lib/ckan/default/bin/paster db dump --config=/etc/ckan/default/production.ini /root/database.sql
```
Then move `/root/database.sql` to the destination host

### On the destination host, shut down apache, clear the database, and load from file
```
service apache2 stop
cd /usr/lib/ckan/default/src/ckan
/usr/lib/ckan/default/bin/paster db clean --config=/etc/ckan/default/production.ini
psql -U ckan_default -h 127.0.0.1 -W -d ckan_default -f /root/database.sql
```
### Restart apache
```
service apache2 start
```
### Re-index search (in /usr/lib/ckan/default/src/ckan)
```
/usr/lib/ckan/default/bin/paster search-index rebuild --config=/etc/ckan/default/production.ini
```
