#!/bin/bash

# this script sets up the server and client reqs for testing in vagrant and also servers and an echobox
# for the ubnt specific scripts on the client, echoing the args to stdout as well as a log file

if [ $(uname -s) != "Linux" ]; then echo "Linux only"; exit 1; fi

case "$1" in
  server)
    debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'
    debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'
    apt-get install -y unzip python-flask python-yaml python-dumbnet python-paramiko python-MySQLdb mysql-server libdumbnet1 apache2 dnsmasq supervisor libapache2-mod-wsgi
    mysql -u root -proot -e "create database playawifi"
    mysql -u root -proot playawifi < /vagrant/schema.sql
    #cp /vagrant/contrib/dnsmasq.conf /etc/
    #service dnsmasq restart
    cp /vagrant/contrib/autoconfig.vhost.conf /etc/apache2/sites-available/000-default.conf
    ln -s /vagrant /var/www/autoconfig
    service apache2 restart
    ln -s /vagrant/contrib/autoconfig.conf /etc/supervisor/conf.d/autoconfig.conf
    supervisorctl reload

  ;;

  client)
    apt-get install -y bridge-utils
    # user ubnt with password ubnt and a uid of 0 (!)
    useradd -G sudo -p '$6$Sa0GC2et$FWcT1vxifJXeUpWz7GulO1UKdKPwgSN8Dm7FRC3g0gv6vT.MZGljxt3ffkbCbvjb3kEuTB7gL8/avagmwEDel1' -u 1000 -g 1000 -o -d /root ubnt
    ln -s /vagrant/vagrant_bootstrap.sh /sbin/ubntbox
    ln -s /vagrant/vagrant_bootstrap.sh /sbin/cfgmtd
    cat /etc/ssh/sshd_config | sed 's/^PermitRootLogin.*$/PermitRootLogin yes/g' > /tmp/sshd_config
    cp /tmp/sshd_config /etc/ssh/sshd_config
    service ssh restart
    brctl addbr br0

  ;;

  *)
    echo "$(date): $1" | tee -a /tmp/output.log
  ;;
 
esac
