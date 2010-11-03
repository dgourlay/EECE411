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
slice_filter = {'name': 'usf_ubc_gnutella2'}

sliceInfo = api_server.GetSlices(auth)

for i in sliceInfo:
	#print 'name:'+i['name']
	print 'id: %d' % i['slice_id']
#print sliceInfo

