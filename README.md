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
2. Clone the [ckanext-odp_theme](https://github.com/azavea/ckanext-odp_theme) and [ckanext-datajson](https://github.com/azavea/ckanext-datajson/) repositories to this directory's parent directory
3. From the project directory, run `ansible-galaxy install -r deployment/ansible/roles.txt -p deployment/ansible/roles`
4. Copy `deployment/ansible/group_vars/vagrant.example` to `vagrant` and edit with your disqus shortname and e-mail credentials. If e-mail credentials are left unconfigured, e-mails will not be sent out.
5. Run `vagrant up`; once the Ansible provisioner finishes, CKAN will be available at http://localhost:8025
6. Creating a sysadmin user:
  ```
  vagrant ssh
  . /usr/lib/ckan/default/bin/activate
  cd /usr/lib/ckan/default/src/ckan
  paster sysadmin add <USERNAME> -c /etc/ckan/default/production.ini
  ```

Deployment
-----------------

1. Launch a server running Ubuntu 12.04. This server should be accessible from the deployment computer over SSH, and should have HTTP and HTTPS access to the internet.
2. Copy `deployment/ansible/hosts/hosts.staging.example` to `hosts.staging` and enter the address of the server that was just launched.
3. Copy `deployment/ansible/group_vars/staging.example` to `staging` and edit any settings you wish to change (see above). Make sure that `ckan_site_url` matches the address at which you will access the site.
4. Run `ANSIBLE_HOST_KEY_CHECKING=false ansible-playbook --private-key=/absolute/path/to/server/key/file.pem --user=ubuntu --inventory-file=deployment/ansible/hosts/hosts.staging deployment/ansible/staging.yml -v`
