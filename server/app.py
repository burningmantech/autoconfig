from flask import Flask, render_template, request, url_for, session, jsonify, g, flash, redirect, escape, Response
from yaml import load
import MySQLdb
import os
import re
import subprocess
try: 
  from dumbnet import arp, addr
except:
  from dnet import arp, addr
import datetime
import paramiko

import threading
import time
import logging
import ubnt2
import sys
import traceback
import time
#@from werkzeug.contrib.fixers import ProxyFix


def printtb():
  fail_line=sys.exc_traceback.tb_lineno
  t,v,tb=sys.exc_info()
  traceback.print_tb(tb)
  l = traceback.extract_tb(tb)
  return traceback.format_list(l)

def get_ip(mac):
  db = MySQLdb.connect(host=configs['db_hostname'], db=configs['db_name'], user=configs['db_username'], passwd=configs['db_password'])
  db.autocommit = True
  cursor = db.cursor()
  mac_select = "select id from assigned_ip where mac = '%s'" % mac
  mac_insert = "insert into assigned_ip (mac) values ('%s')" % mac

  ip = 0
  try:
    cursor.execute(mac_select)
    ip = int(cursor.fetchone()[0])
    print "Returning existing IP"
  except: 
    cursor.execute(mac_insert)
    db.commit()
    cursor.execute(mac_select)
    ip = int(cursor.fetchone()[0])

  print "Got IP(id) = ", ip

  ip_dot  = (ip % 200) + 50
  ip_dot = "192.168.1.%d" % ip_dot
  return ip_dot


def parse_yaml_configs():
  try:
    return load(open('secrets.dev.yml'))
  except:
    return load(open('secrets.yml'))

def connect_db():
  app.logger.debug('Connecting to the DB')
  db = MySQLdb.connect(host=configs['db_hostname'], db=configs['db_name'], user=configs['db_username'], passwd=configs['db_password'])
  db.autocommit = True
  return db

def get_db():
  if not hasattr(g, 'db'):
    g.db = connect_db()
  return g.db

def get_mac():
  app.logger.debug('get_mac')
  arpTable = arp()
  session['ip'] = request.environ['REMOTE_ADDR']
  session['mac'] = str(arpTable.get(pa=addr(session['ip'])))
  return(session)
  
def get_quad(hour, min):
  app.logger.debug('get_quad')
  p = datetime.time(int(hour), int(min))
  quad0 = datetime.time(2,0)
  quad1 = datetime.time(4,0)
  quad2 = datetime.time(6,0)
  quad3 = datetime.time(8,0)
  if quad0 <= p <= quad1:
    pq = configs['quad0']
  elif quad1 <= p <= quad2:
    pq = configs['quad1']
  elif quad2 <= p <= quad3:
    pq = configs['quad2']
  else:
    pq = configs['quad3']
  return(pq)

BASEDIR = os.path.abspath(os.path.dirname(__file__))
STATICDIR = os.path.join(BASEDIR, '../static')
TEMPLATEDIR = os.path.join(BASEDIR, '../templates')

app = Flask(__name__, static_folder=STATICDIR, template_folder=TEMPLATEDIR)

#app.wsgi_app = ProxyFix(app.wsgi_app)

@app.teardown_appcontext
def close_db(error):
  if hasattr(g, 'db'):
    g.db.close()

configs = parse_yaml_configs()
app.config['SECRET_KEY'] = configs['secret_key']
app.debug = configs['debug']

app.logger.debug('yml configs: %s' % configs)
app.logger.debug('app configs: %s' % app.config)

@app.route('/')
def slash():
  get_mac()
  app.logger.debug("ip = %s, mac = %s" % (session['ip'], session['mac']))
  return render_template('index.html', session=session)

#@app.errorhandler(404)
#def page_not_found(e):
  #return render_template('index.html', session=session), 404

@app.route('/_reg', methods=['POST'])
def reg():
  session['hour'] = request.form['hour']
  session['minute'] = request.form['minute']
  session['radial'] = request.form['radial']
  session['camp'] = escape(request.form['camp'])
  session['emac'] = request.form['mac']
  session['radio'] = request.form['radio']
  session['contact'] = escape(request.form['contact'])
  session['email'] = escape(request.form['email'])
  session['quad'] = get_quad(session['hour'], session['minute'])
  p_insert = "insert into participants\
              (hour, minute, radial, quad, mac, camp, contact, email, created_at) \
              values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', now())" % \
              (session['hour'], session['minute'], session['radial'], session['quad'], session['emac'], session['camp'], session['contact'], session['email'])
  p_id_val = "select id from participants where mac = '%s'" % session['emac']
  app.logger.debug(p_insert)
  db = get_db()
  cursor = db.cursor()
  try:
    try: 
      cursor.execute(p_insert)
      db.commit()
      cursor.execute(p_id_val)
      session['p_id'] = int(cursor.fetchone()[0])
    except:
      cursor.execute(p_id_val)
      session['p_id'] = int(cursor.fetchone()[0])
  except MySQLdb.Error as myerr:
    app.logger.debug('mysql error: %s' % myerr)
    flash('There was an error: %s' % myerr, 'error')
  except Exception, e:
    flash('Error processing request: %s' % e, 'error')

  print "Got session p_id", session['p_id']

  try: 
    v_insert = "insert into vlans (assigned_to) values ('%s')" % session['p_id']
    v_ass = "select vlan_id from vlans where assigned_to = '%s'" % session['p_id']
  except MySQLdb.Error as myerr:
    flash('Error getting p_id: %s' % myerr, 'error')
    return render_template('config.html', session=session)

  try:
    try: 
      cursor.execute(v_insert)
      db.commit()
    except: 
      pass
    cursor.execute(v_ass)

    session['v_id'] = cursor.fetchone()[0]
    app.logger.debug('v_id: %s' % session['v_id'])    

    session['v_ip'] = str(int(session['v_id'])-999)
    app.logger.debug('v_ip: %s' % session['v_ip'])    

    session['v_ip_low'] = str(int(session['v_ip'])%256)
    app.logger.debug('v_ip_low: %s' % session['v_ip_low'])  

    session['v_ip_high'] = str(int(session['v_ip'])/256)
    app.logger.debug('v_ip_high: %s' % session['v_ip_high'])

    session['v_ip_high2'] = str(101+(int(session['v_ip'])/256))
    app.logger.debug('v_ip_high2: %s' % session['v_ip_high2'])

    print "Set v_ip to %s" % session['v_ip']
  except MySQLdb.Error as myerr:
    app.logger.debug('mysql error: %s' % myerr)
    flash('There was an error: %s' % myerr, 'error')
  except Exception, e:
    flash('Error processing request (vlans): %s' % e, 'error')
    
  flash('Your information was collected', 'info')

  mac = session['emac']
  ip = get_ip( mac )
  session['eip'] = ip
  session['firmware'] = session['radio']

  try: 
    session.update(configs['secrets'])
    app.logger.debug(session)
    config = ubnt2.generate_config(session)
  except Exception, e: 
    printtb()
    try: 
      flash('Error configuring AP: %s' % str(e), 'error')
    except:
      flash('Unhandled Error configuring AP', 'error')

  # returning the config as a text file becasue we are tired
  return Response(config, mimetype="application/octet-stream'",
                          headers={"Content-Disposition": "attachment;filename=%s.conf" % session['v_id']})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port = configs['port'], use_reloader = False, debug = configs['debug'])
