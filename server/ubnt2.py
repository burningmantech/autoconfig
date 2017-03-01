import paramiko
import md5
import os
import collections
import time

def set_status(mac, msg, percent, db, cursor):
  stmt = """  UPDATE assigned_ip
              SET percent='%s',msg='%s'
              WHERE mac='%s'; 
         """ % ( percent, msg, mac )

  print "Status is now '%s', percent=%s" % (msg, percent)
  cursor.execute(stmt)
  db.commit()

def get_status( mac, db, cursor):
  stmt = """  SELECT msg, percent 
              FROM assigned_ip 
              WHERE mac='%s'; 
         """ % ( mac )

  cursor.execute(stmt)
  ret = cursor.fetchone() 
  return ret
 

def upgrade_firmware(session, db, cursor):
  firmware_path = "static/firmware"
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
  print("session['eip'] = %s" % session['eip'])
  try: 
    ssh.connect(session['eip'], 22, 'ubnt', 'ubnt', timeout=5, allow_agent=False, look_for_keys=False)
  except:
    ssh.connect(session['eip'], 22, 'ubnt', 'ubnt', timeout=5, allow_agent=False, look_for_keys=False)
  stdin, stdout, stderr = ssh.exec_command('/sbin/ubntbox mca-status', timeout=10)
  firmware_locations = list(os.walk(firmware_path))[0][2]
  firmware_locations = dict( [ (x[:2],"%s/%s" % (firmware_path,x) ) for x in firmware_locations ] )

  firmware_device = {s.split('=')[0] : s.split('=')[1] for s in stdout.readline().strip().split(',')}['firmwareVersion']

  print firmware_device
  if not firmware_locations.has_key(firmware_device[:2]):
    msg = "No firmware found for device %s" % firmware_device
    print msg
    return msg

  session["firmware"] = firmware_device[:2]

  set_status(session["emac"], "Updating firmware for device %s" % firmware_device, "10", db, cursor)

  firmware_bytes = None
  with open(firmware_locations[firmware_device[:2]], "rb") as f:
    firmware_bytes = f.read()
    
  m = md5.new()
  m.update(firmware_bytes)
  md5_client = m.hexdigest()

  
  print "Upload firmware %s md5=%s: " % (firmware_locations[firmware_device[:2]], md5_client)

  stdin, stdout, stderr = ssh.exec_command("dd of=/tmp/newfw.bin", timeout=120)
  stdin.write(firmware_bytes)
  stdin.close()

  set_status(session["emac"], "Firmware upload complete, verify image", "15", db, cursor)
  print "Upload complete, checking file"

  stdin, stdout, stderr = ssh.exec_command("md5sum /tmp/newfw.bin", timeout=30)

  md5_server = stdout.read().strip()
  md5_server = md5_server.split(" ")[0]

  if (md5_client != md5_server):
    msg = "No firmware found for device %s" % firmware_device
    print msg
    return msg

  print "Got MD5 match on upload" 
  stdin, stdout, stderr = ssh.exec_command('/sbin/ubntbox fwupdate.real -c /tmp/newfw.bin', timeout=10)
  stdin.close()
  
  o=stdout.read()
  e=stderr.read()

  if o or e: 
    msg = "Bad fwupdate check %s %s" % (o, e)
    print msg
    return msg

  set_status(session["emac"], "Firmware verified, flashing image. This can be slow!", "20", db, cursor)

  print "fwupdate returned OK, will flash" 
  stdin, stdout, stderr = ssh.exec_command('/sbin/ubntbox fwupdate.real -m /tmp/newfw.bin', timeout=90)

  while 1: 
    # We don't have a good exit condition. We either wait for done or timeout. 
    try: 
      res = stderr.readline()
      print res
      if "done" in res.lower():
        break
    except: 
      break

  #print "..."
  #got_data = True
  #while got_data: 
  #  got_data = False
  #  line = stderr.readline()
  #  print "..", line
  #  if len(line) > 0:
  #    got_data=True

  ssh.close()

  set_status(session["emac"], "Firmware updated. Please wait while radio reboots.", "25", db, cursor)

  return None

def generate_config(session):
  template = None
  try:
    with open("templates/%s.config" % session["firmware"], "rb") as f:
      template = f.read()
  except: 
    raise ValueError("No configuration found for your radio.")

  # Here we use python string formatting to apply a configuration. This should
  # be changed to use a real template. 

  template = template % session

  return template

  # 

  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

  start = time.time()
  time.sleep(0.1)

  while 1: 
    try: 
      if (time.time() - start) > 90:
        raise ValueError("Giving up trying to reach ip=%s" % session['eip'])
      try:
        ssh.connect(session['eip'], 22, 'ubnt', 'ubnt', timeout=5, allow_agent=False, look_for_keys=False)
      except:
        ssh.connect(session['eip'], 22, 'ubnt', 'ubnt2', timeout=5, allow_agent=False, look_for_keys=False)
      break
    except: 
      time.sleep(1)

  set_status(session["emac"], "Radio has rebooted. Applying configuration.", "30", db, cursor)

  """
  # XXX: This code was based on the idea of fetching a configuration from a
  #      a radio and then applying a set of configuration changes-- We didn't
  #      have time to test if this actually worked or not, so we instead went
  #      with one configuration per radio. 
  #
  #      From here on we should just directly apply our configuration from 
  #      configuration template above.
 
  stdin, stdout, stderr = ssh.exec_command('cat /tmp/running.cfg', timeout=10)
  cfg_file = stdout.read()

  if len(cfg_file) < 20: 
    raise ValueError("Getting running config from AP")

  cfg = collections.OrderedDict()
  
  for line in cfg_file.splitlines():
    try: 
      k,v = line.split("=", 1)
      cfg[k] = v
    except: 
      pass

  for line in template.splitlines():
    try: 
      k,v = line.split("=", 1)
      cfg[k] = v
    except: 
      pass

  new_cfg = "\n".join([ "=".join(x) for x in cfg.items() ])

  print new_cfg
  """

  print "I am assigning VLAN=%s, QUAD=%s" % (session["v_id"], session["quad"])

  stdin, stdout, stderr = ssh.exec_command('sort > /tmp/running.cfg', timeout=10)
  print template
  stdin.write(template)
  stdin.close()

  stdin, stdout, stderr = ssh.exec_command('cp /tmp/running.cfg /tmp/system.cfg', timeout=10)
  stdin, stdout, stderr = ssh.exec_command('cfgmtd -w -f /tmp/running.cfg -p /etc/', timeout=10)
  stdin.close()
  print "cfgmtd:", stdout.read()
  time.sleep(2)

  set_status(session["emac"], "Configuration applied. Please wait as radio applies new configuration.", "35", db, cursor)
  stdin, stdout, stderr = ssh.exec_command('reboot', timeout=10)



  ssh.close()

  print "Maybe we should verify radio is up at this point"
  
#TEST for config. 
#
# BROKEN! add correct ...
#
#session={ 'quad': 'empty-quad', 
#          'v_id': '666', 
#          'eip': '192.168.1.52'
#        }
#
#generate_config(session)
 
