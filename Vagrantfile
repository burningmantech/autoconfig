# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "debian/jessie64"
  #config.hostmanager.enabled = true

  config.vm.provider "virtualbox" do |vb|
    vb.memory = 512
    vb.cpus = 1
  end

  config.vm.define :server do |sub_config|
    sub_config.vm.network :private_network, ip: "192.168.1.2",
      virtualbox__intnet: "autoconfig"
    sub_config.vm.hostname = 'server'
    sub_config.vm.network :forwarded_port, guest: 80, host: 8888
    sub_config.vm.network :forwarded_port, guest: 3306, host: 33306
    sub_config.vm.provision :shell, path: "vagrant_bootstrap.sh", args: "server"
  end

  config.vm.define :client do |sub_config|
    sub_config.vm.network :private_network, ip: "192.168.1.20",
      virtualbox__intnet: "autoconfig"
    sub_config.vm.hostname = 'client'
    sub_config.vm.provision :shell, path: "vagrant_bootstrap.sh", args: "client"
  end

end
