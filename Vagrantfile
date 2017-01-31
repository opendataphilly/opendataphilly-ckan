# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 1.6"

require "yaml"

# Deserialize Ansible Galaxy installation metadata for a role
def galaxy_install_info(role_name)
  role_path = File.join("deployment", "ansible", "roles", role_name)
  galaxy_install_info = File.join(role_path, "meta", ".galaxy_install_info")

  if (File.directory?(role_path) || File.symlink?(role_path)) && File.exists?(galaxy_install_info)
    YAML.load_file(galaxy_install_info)
  else
    { install_date: "", version: "0.0.0" }
  end
end

# Uses the contents of roles.yml to ensure that ansible-galaxy is run
# if any dependencies are missing
def install_dependent_roles
  ansible_directory = File.join("deployment", "ansible")
  ansible_roles_spec = File.join(ansible_directory, "roles.yml")

  YAML.load_file(ansible_roles_spec).each do |role|
    role_name = role["src"]
    role_version = role["version"]
    role_path = File.join(ansible_directory, "roles", role_name)
    galaxy_metadata = galaxy_install_info(role_name)

    if galaxy_metadata["version"] != role_version.strip
      unless system("ansible-galaxy install -f -r #{ansible_roles_spec} -p #{File.dirname(role_path)}")
        $stderr.puts "\nERROR: An attempt to install Ansible role dependencies failed."
        exit(1)
      end

      break
    end
  end
end

# Install missing role dependencies based on the contents of roles.yml
if [ "up", "provision" ].include?(ARGV.first)
  install_dependent_roles
end

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provider :virtualbox do |vb|
    vb.memory = 1024
  end

  config.vm.network "forwarded_port", guest: 8080, host: 8025
  config.vm.network "private_network", ip: "192.168.8.85"

  config.vm.synced_folder "../ckanext-odp_theme", "/vagrant_ckanext-odp_theme", nfs: true
  config.vm.synced_folder "../ckanext-datajson", "/vagrant_ckanext-datajson", nfs: true

  config.vm.provision :ansible do |ansible|
    ansible.playbook = "deployment/ansible/site.yml"
    ansible.verbose = 'v'
    ansible.inventory_path = "deployment/ansible/hosts/hosts.vagrant"
    ansible.limit = 'all'
  end
end
