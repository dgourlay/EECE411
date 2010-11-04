import subprocess
import commands
import os

login = 'usf_ubc_gnutella2'
cogPath = '/home/'+login+'/PL/Cogs/mon01/'

os.system('rm -rf /home/'+login+'/output/')
os.system('mkdir /home/'+login+'/output/')
os.system('sudo python '+cogPath+'node.py')

#subprocess.Popen([r"sudo","python", cogPath+'node.py'])

