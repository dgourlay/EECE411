#! /usr/bin/env python
import xmlrpclib
api_server = xmlrpclib.ServerProxy('https://www.planet-lab.org/PLCAPI/', allow_none=True)
# Create an empty dictionary (XML-RPC struct)
auth = {}
# Specify password authentication
auth['AuthMethod'] = 'password'
# Username and password
auth['Username'] = 'dgourlay@interchange.ubc.ca'
auth['AuthString'] = 'snooker'
authorized = api_server.AuthCheck(auth)
if authorized:
	print 'We are authorized!'

# This may take a while.
all_nodes = api_server.GetNodes(auth)
nodeID = 21971
for i in all_nodes:
	ids = i['slice_ids']
	if nodeID in ids:
		print i['boot_state']

#print all_nodes

