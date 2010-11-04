#! /usr/bin/env python
import subprocess

login = 'usf_ubc_gnutella2'
tarName = 'jre.tar.gz'
cogPath = '/home/'+login+'/PL/Cogs/cog01/'
# extract JRE
subprocess.Popen([r"wget", "-N", "http://www.ece.ubc.ca/~samera/TA/411/project/jre.tar.gz"]).wait()
subprocess.Popen([r"tar", "xvzf", tarName]).wait()
subprocess.Popen([r"mv", cogPath+'bash_profile', "/home/"+login+"/.bash_profile"]).wait()

