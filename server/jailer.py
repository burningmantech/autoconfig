import app
import time
import paramiko
import multiprocessing
try: 
  from dumbnet import arp, addr
except:
  from dnet import arp, addr
import datetime

jail_ap_count=0

def jail_ap(lock,value):
  global jail_ap_count

  print("%s: starting jailer" % datetime.datetime.now())
  print lock, value

  while 1: 
    with lock:
      value.value += 1

    time.sleep(1)
    arpTable = arp()
    
    try: 
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
      ssh.connect("192.168.1.20", 22, 'ubnt', 'ubnt', timeout=5, allow_agent=False, look_for_keys=False)
      print "Connected to 192.168.1.20"

      mac = str(arpTable.get(addr('192.168.1.20')))
      print "MAC IS", mac

      if mac == "None":
        print "XXX: Error getting MAC Address"
        continue

      print "Applying jail IP to '%s'" % mac
      p_id = None

      # the actual jailing of the default config.
      # the IP of the autoconfig server, or whatever is providing captive dns
      # should be used for the nameserver
      ip_dot = app.get_ip(mac)
      ssh.exec_command("ip addr add %s/24 dev br0" % ip_dot, timeout=5)
      print(" ip %s added" % ip_dot)
      ssh.exec_command("sysctl -w net.ipv4.conf.br0.promote_secondaries=1", timeout=5)
      print(" sysctl changed")
      ssh.exec_command("echo 'nameserver 192.168.1.10' > /etc/resolv.conf", timeout=5)
      print(" nameserver added")
      ssh.exec_command("ip addr delete 192.168.1.20/24 dev br0", timeout=5)
      print(" primary ip deleted")
      ssh.close()

      print "%s: Connected to AP and applied IP %s" % (datetime.datetime.now(), ip_dot)
    except Exception, e:
      print e
      if "Authentication failed." in str(e):
        arpTable.delete('192.168.1.20')
        print "%s: Error trying to jail AP" % datetime.datetime.now() , e
      pass 


def start_jailer(v,l):
  jailer = multiprocessing.Process(target=jail_ap, args=(l,v))
  jailer.start()
  return jailer

v = multiprocessing.Value('i', 0)
l = multiprocessing.Lock()
jailer = start_jailer(v,l)

while 1:
  newVal = 0
  oldVal = 0
  with l:
    newVal = v.value

  time.sleep(15) 
  with l:
    oldVal = v.value


  if (newVal == oldVal) or not jailer.is_alive():
    
    arpTable.delete(arp('192.168.1.20'))
    v = multiprocessing.Value('i', 0)
    l = multiprocessing.Lock()
    try:
      jailer.terminate()
    except:
      pass
    jailer = start_jailer(v, l)
    print "restarting jailer"
