# autoconfig
This was Burning Man's 2016 autoconfiguration tool, which configured
participant radio's to use the Burning Man WiFi network. 

It's written in Python using Flask and a MySQL backend. 

It is designed to work as follows: 

* Participant resets radio to default configuration. 
* Participant Radio Connects to BM WiFi. 
* Jailer Service (jailer.py) connects to Participant Radio, changes default IP
  from 192.168.1.20 to 192.168.1.1xx. Jailer.py is run as a regular process
  seperate from Flask App. 
* Participant loads any web page, Captive Portal web page is displayed asking
  participant for information. 
* The information is used to lock the Participant radio to a specific BM
  sector radio as well as well as provide contact information to the BM IT
  team to help diagnose network problems.
* Participant submits information, a configuration is created for the
  specific radio model, and that configuration is pushed onto the radio.
* Radio resets automatically, and should not be able to connect to BM WiFi.
  Connection is provided via Ethernet using DHCP for connected computers. 
* Participants are encouraged to share the connection per the WiFi
  guidelines. ( 2.4 Ghz Only, low power, open network w/ camp name in SSID)
  

Run for local dev with:

```
export FLASK_APP=./server/app.py
flask run
```
Use a wsgi container for production. See contrib/autoconfig.wsgi for an apache2 example

From a default-ish Debian 8 install:

```
apt-get install -y unzip python-flask python-yaml python-dumbnet python-paramiko python-MySQLdb mysql-server libdumbnet1
```

Note that Debian renamed libdnet to libdumbnet. Install as appropriate to your distribution

```
mysql -u root -proot -e "create database playawifi"
mysql -u root -proot playawifi < schema.sql
```

Example get device strings:

```
deviceName=PowerBeam M5 300,deviceId=24:A4:3C:F2:51:25,firmwareVersion=XW.ar934x.v6.0-beta10.29223.160601.1516,platform=PowerBeam M5,deviceIp=192.168.1.20
deviceName=NanoBridge M5,deviceId=00:27:22:50:03:24,firmwareVersion=XM.ar7240.v5.6.8.29413.160715.1613,platform=NanoBridge M5,deviceIp=192.168.1.20
deviceName=NanoBeam 5AC 19,deviceId=80:2A:A8:24:D1:51,firmwareVersion=XC.qca955x.v8.0-beta15-cs.31340.160729.1158,platform=NanoBeam 5AC 19,deviceIp=192.168.1.20
```

Example firmwares:

```
PowerBeam M5 300 = XW.v6.0.30097.161219.1705.bin
NanoBridge M5    = XM.v6.0.30097.161219.1716.bin
NanoBeam 5AC 19  = XC.v8.0.1.32631.170202.1626.bin
```

