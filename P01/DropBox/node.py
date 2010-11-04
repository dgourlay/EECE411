# imports
import os
import socket
import string
import random
import thread
import time
import map # custom script

# constants
PORT = 5001
CONNECT_TIMEOUT = 10
MAX_SLEEP_TIME = 10
EOF = "EOF"
BUSY_SIGNAL = "=SERVRBUSY="
OKAY_SIGNAL = "=SERVROKAY="
REVFILE = 'rev.txt'

# global vars
numNodes = 0
nodes = [] # list of nodes
nodeStatus = {} # map of all nodes and statuses
rev = 0 # revision number acts as logical clock, should this be int?
lock = thread.allocate_lock() # used for synchronization; ensures that node is either acting either as client or server at one time

# load node list from file
def loadNodes():
	global nodes, numNodes
	tempData = open("nodes.txt").read()
	nodes = string.split(tempData, "\n") #node is now a list of nodes 
	numNodes = len(nodes)

# updates status & revision of own node; should be run for every successful connection
def updateStatusAndRevision():
	global rev, nodeStatus
	rev += 1
	# update our own status
	map.updateOwnStatus(nodeStatus, rev)
	# write revision number to file
	f = open(REVFILE, 'w')
	f.write(repr(rev))
	f.close()

# returns status received from socket; returns none if receive fails
def receiveStatus(s):
	total_data=[]; data=None
	while True:
		try :
			data = s.recv(8192)
		except socket.error, err: # i.e. if receive times out
			return None
		if EOF in data:
			total_data.append(data[:data.find(EOF)])
			break
		total_data.append(data)
		if len(total_data) > 1:
			# check EOF was split 
			last_pair = total_data[-2] + total_data[-1]
			if EOF in last_pair: 
				total_data[-2] = last_pair[:last_pair.find(EOF)]
				total_data.pop()
				break
	return eval(''.join(total_data))
	

# client thread:
# connect
# acquire lock
# get map from server
# increment rev #, etc.
# do update
# send update to server
# release lock
# sleep for random time
def clientThread() :
	global lock, nodeStatus
	cs = None
	
	while True :
		# take a break
		time.sleep(random.randrange(0, MAX_SLEEP_TIME))
		
		while True: # we want to keep trying until one connection has been made
			# acquire lock
			lock.acquire()
			print "== Now acting as 'client' =="
		
			# make a connection to a random node
			target = nodes[random.randrange(0, numNodes)]
			
			try :
				print "Connecting to " + target + "..."
				cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				cs.settimeout(CONNECT_TIMEOUT)
			except socket.error, err:
				# failing to create socket is a bad sign...something else is afoot here...
				# print the error and stop this thread
				print err
				lock.release() # make sure we reliniquish the lock first!
				return # stop the thread
			
			try :
				cs.connect((target, PORT))
			except socket.error, err:
				# connection to target failed; assume dead
				print "Node " + target + " has failed. Updating status..."
				map.setDeadFlag(nodeStatus, target)
				cs.close()
				lock.release() # release lock first!
				break # go back to sleep; we're done with this round
				
			try:
				signal = cs.recv(len(OKAY_SIGNAL))
				
				if signal == BUSY_SIGNAL:
					print "Node busy...let's try another one"
					cs.close()
					lock.release() # make sure we reliniquish the lock first!
					continue # retry
				elif signal == OKAY_SIGNAL:
					print "Connection established! Initiating exchange..."
					
					# receive the map from the node
					otherStatus = receiveStatus(cs)
					
					if otherStatus == None:
						# the status was not received for some reason...let's disconnect and try another node
						print "Status not received from node...let's try another one"
						cs.close()
						lock.release() # make sure we reliniquish the lock first!
						continue # retry
					
					# before we do anything, update our own status
					updateStatusAndRevision()
					# synchronizes the two nodes
					map.doUpdate(nodeStatus, otherStatus)
					
					print "Status updated: at revision " + str(rev)
					print nodeStatus

					# update the other node with the new status
					cs.send(repr(nodeStatus))
					cs.send(EOF)
					
					# we are done; close the connection
					cs.close()
					# release lock
					lock.release()
					break
				else:
					print "Received unexpected signal from node...let's try another one"
					cs.close()
					lock.release() # make sure we reliniquish the lock first!
					continue # retry
			except socket.error, err:
				# we weren't able to update the other's list for some reason...but at least we updated our own
				print err
				cs.close()
				lock.release() # make sure we reliniquish the lock first!
				continue # retry
		# end while - at least one connection has been made
	# end while

# spinoff thread to handle server connections:
# acquire lock
# receive instruction from client
# send map to client
# wait...
# get map from client & update
# release lock
def serviceThread(cs, addr) :
	global lock, nodeStatus
	
	cs.settimeout(CONNECT_TIMEOUT) # enforce a timeout
	
	# try to acquire the lock, if it's not available send busy signal to client
	if lock.acquire(0):
		print "== Now acting as 'server' =="
		
		# send OK signal to client
		cs.send(OKAY_SIGNAL)
		
		cs.send(repr(nodeStatus))
		cs.send(EOF)
	
		tempStatus = receiveStatus(cs)
		
		if tempStatus == None:
			# we can't be sure whether the client has already updated, and there are simply connection problems, or...?
			# but there's not much we can do about it
			print "Connection error: failed to receive update from client"
		else:
			nodeStatus = tempStatus
			print "Status updated!"
			print nodeStatus
		
		# relinquish lock
		lock.release()
	else:
		cs.send(BUSY_SIGNAL)
		
	cs.close()
	
	
# ***************************************************************
# program begin
# ***************************************************************
def main():
	print "******************************"
	print "Monitoring script initialized"
	print "******************************"
	
	# load the nodes into memory
	loadNodes()
	
	# read rev from file if possible 
	try:
		f = open(REVFILE, 'r')
		rev = string._int(f.readline())
		f.close()
	except IOError:
		# file does not exist, rev = 0
		rev = 0

	# spawn client thread to periodically 
	print "Spawning 'client' thread to handle outbound connections..."
	thread.start_new_thread(clientThread, ()) # or should we use main threading module?

	# TODO: how to restart if failed?
	print "Setting up 'server' socket to handle inbound connections..."
	try:
		ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error, err:
		# failing to create socket is a bad sign...something else is afoot here...
		print err
		return
	try:
		ss.bind(("", PORT))
		ss.listen(5) # maximum number of waiting nodes is usually 5
	except socket.error, err:
		ss.close()
		print err
		return
	while True:
		# keep spinning off new threads to handle requests
		thread.start_new_thread(serviceThread, tuple(ss.accept()))

# For local testing only...
# To test on real nodes we only need to call main()
#loadNodes()
main() # either call this
#clientThread() # or this, but not both