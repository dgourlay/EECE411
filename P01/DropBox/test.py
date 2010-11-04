import string
tempData = open('nodeList.txt').read()
f = open('newNodes.txt', 'a')
nodes = string.split(tempData, "\r") #node is now a list of nodes

for i in nodes: 
	f.write("scp -r ~/Dropbox/eece411/P01 usf_ubc_gnutella2@"+i+":~/ \n")
	
f.close();