The included vagrantfile will create 2 hosts, a server and a client.

The server will run the jailer app via supervisor and the web app via apache and mod_wsgi 

Port 80 is forwarded to 8888, 22 to 2202 (typical), and 3306 to 33306

The client has a empty br0 and a user of ubnt with a password of ubnt, and will be constantly updated via the jailer app

ie:

```
vagrant up

vagrant ssh client
  ip addr

vagrant ssh server
  tail -f /var/log/autoconfig.*
  supervisorctl stop autoconfig
  service apache2 restart

vagrant destroy -f
```

dnsmasq is not started