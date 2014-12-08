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
2. From the project directory, run `ansible-galaxy install -r deployment/ansible/roles.txt -p deployment/ansible/roles`
3. Copy deployment/ansible/hosts/hosts.vagrant.example to hosts.vagrant and edit with your disqus shortname and e-mail credentials. If e-mail credentials are left unconfigured, e-mails will not be sent out.
4. Run `vagrant up`; CKAN will be available at on port 8025.
5. Creating a sysadmin user:
  ```
  vagrant ssh
  . /usr/lib/ckan/default/bin/activate
  cd /usr/lib/ckan/default/src/ckan
  paster sysadmin add <USERNAME> -c /etc/ckan/default/production.ini
  ```
