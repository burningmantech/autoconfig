import os
import sys
os.chdir('/var/www/autoconfig')
sys.path.insert(0, '/var/www/autoconfig')

from server.app import app as application
