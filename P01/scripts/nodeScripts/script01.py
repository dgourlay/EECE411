#! /usr/bin/env python
import subprocess

nodeListPath = '../nodeTest.txt'
distFile = '../README.txt'
login = 'usf_ubc_gnutella2'
destPath=':/home/'+login

#functions

#return # of lines in a file
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
        	pass
    return i + 1

def post_scp(line):
    subprocess.Popen([r"ssh",login+'@'+line]).wait()
    subprocess.Popen([r"echo",'Hello World']).wait()
    subprocess.Popen([r"exit"]).wait()

# subprocess.Popen([r"echo","Starting script"])
date=subprocess.Popen([r"date"], stdout=subprocess.PIPE).communicate()

#load nodelist from file
print 'STARTING <'+date[0].rstrip()+'>'
fileLength = file_len(nodeListPath)
print '%d nodes loaded from file' % (fileLength, )
nodeList = open(nodeListPath)

#iterate sending distFile through nodelist
index=0

for line in nodeList:
#print line,
	line = line.rstrip()
	print '[',index, '] scp ',distFile,'to ', line,
	subprocess.Popen([r"scp",distFile,login+'@'+line+destPath]).wait()
	#do something with the file
	post_scp(line)
	index = index + 1

nodeList.close()
