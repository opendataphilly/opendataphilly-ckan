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
3. Copy deployment/ansible/site.yml.example to main.yml and edit with your disqus shortname
4. Run `vagrant up`; CKAN will be available at on port 8025.
