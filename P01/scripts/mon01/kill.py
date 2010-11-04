import subprocess
import commands
import os

login = 'usf_ubc_gnutella2'
cogPath = '/home/'+login+'/PL/Cogs/mon01/'


os.chdir(cogPath)
subprocess.call("sudo ./kill.sh", executable="bash", shell=True)
#os.system('sudo ./kill.sh')
os.chdir("/home/usf_ubc_gnutella2/")

