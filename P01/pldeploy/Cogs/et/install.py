#! /usr/bin/env python
import subprocess
import os

login = 'usf_ubc_gnutella2'
tarPath = 'http://effbot.org/media/downloads/elementtree-1.2.6-20050316.tar.gz'
tarName = 'elementtree-1.2.6-20050316.tar.gz'
folderName = 'elementtree-1.2.6-20050316'
cogPath = '/home/'+login+'/PL/Cogs/cog01/'
# extract JRE
subprocess.Popen([r"wget", "-N", tarPath]).wait()
subprocess.Popen([r"tar", "xvzf", tarName]).wait()
os.chdir(folderName)
subprocess.Popen([r"sudo","python","setup.py", "install"]).wait()

