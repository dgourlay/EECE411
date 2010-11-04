# UBC - EECE 411
# PlanetLab Monitoring Service
# By: Derek Gourlay, Paul Chiu, Isaiah Ng, Will Chang
#
VERSION = "1.0" # this should be updated every time we deploy a new script

# imports
import os
import sys
import socket
import string
import random
import thread
import time
import xml # custom scripts
import map

# constants
PORT = 5011
CONNECT_TIMEOUT = 10
MIN_SLEEP_TIME = 5
MAX_SLEEP_TIME = 10
EOF = "EOF"
BUSY_SIGNAL = "=SERVRBUSY="
CLIENT_RPLY = "=RECEIVED="
CLK_FILE = "output/clock"
NODE_FILE = "/home/usf_ubc_gnutella2/PL/Cogs/mon01/nodes.txt"

# global vars
numNodes = 0
nodes = [] # list of nodes
nodeStatus = {} # map of all nodes and statuses
clk = 0 # logical clock to make sure nodes alway have the latest status
lock = thread.allocate_lock() # used for synchronization; ensures that node is either acting either as client or server at one time

# load node list from file
def loadNodes():
	global nodes, numNodes
	tempData = open(NODE_FILE).read()
	nodes = string.split(tempData, "\n") #node is now a list of nodes 
	numNodes = len(nodes)

# updates status & clock of own node
def updateSelf():
	global clk, nodeStatus
	clk += 1
	# update our own status
	map.updateOwnStatus(nodeStatus, clk)
	# write clock to file
	f = open(CLK_FILE, 'w')
	f.write(repr(clk))
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
# acquire lock
# connect
# get map from server
# increment rev #, update self
# do update
# send update to server
# release lock
# sleep for random time
def clientThread() :
	global lock, nodeStatus
	cs = None
	
	while True :
		# take a break
		time.sleep(random.randrange(MIN_SLEEP_TIME, MAX_SLEEP_TIME))
		
		while True: # we want to keep trying until one connection has been made
			# acquire lock
			lock.acquire()
			print "== Locked as: Client =="
		
			# make a connection to a random node
			target = nodes[random.randrange(0, numNodes)]
			
			try :
				print "Connecting to " + target + "..."
				cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				cs.settimeout(CONNECT_TIMEOUT)
			except socket.error, err:
				# failing to create socket is a bad sign...something else is afoot here...
				print err
				lock.release() # make sure we reliniquish the lock first!
				print "== Lock relinquished =="
				sys.exit(1) # kill the process
			
			try :
				cs.connect((target, PORT))
			except socket.error, err:
				# connection to target failed; assume dead
				print "Node " + target + " has failed. Updating status..."
				map.setDeadFlag(nodeStatus, target)
				xml.dumpToXML(nodeStatus)
				cs.close()
				lock.release() # release lock first!
				print "== Lock relinquished =="
				break # go back to sleep; we're done with this round
				
			try:
				signal = cs.recv(max(len(BUSY_SIGNAL), len(VERSION)))
				cs.send(CLIENT_RPLY)
				
				if signal == BUSY_SIGNAL:
					print "Node busy...let's try another one"
					cs.close()
					lock.release() # make sure we reliniquish the lock first!
					print "== Lock relinquished =="
					continue # retry
				elif signal == VERSION: # we want to make sure that we only talk with servers with the same version number
					print "Connection established! Initiating exchange..."
					
					# receive the map from the node
					otherStatus = receiveStatus(cs)
					
					if otherStatus == None:
						# the status was not received for some reason...let's disconnect and try another node
						print "Status not received from node...let's try another one"
						cs.close()
						lock.release() # make sure we reliniquish the lock first!
						print "== Lock relinquished =="
						continue # retry
					
					# before we do anything, update our own status
					updateSelf()
					# synchronizes the two nodes
					map.doUpdate(nodeStatus, otherStatus)
					
					print "Status updated! Writing to XML..."
					xml.dumpToXML(nodeStatus)

					try:
						# update the other node with the new status
						cs.send(repr(nodeStatus))
						cs.send(EOF)
					except socket.error, err:
						print err # we don't know why sending failed, but at least we have the updated status
					
					# we are done; close the connection
					cs.close()
					# release lock
					lock.release()
					print "== Lock relinquished =="
					break
					
				else: # either the sending failed or the version number is incorrect; disconnect and try again
					print "Version mismatch: ours - " + VERSION + "; theirs - " + signal
					cs.close()
					lock.release() # make sure we reliniquish the lock first!
					print "== Lock relinquished =="
					continue # retry
			except socket.error, err:
				# we weren't able to update the other's list for some reason...but at least we updated our own
				print err
				cs.close()
				lock.release() # make sure we reliniquish the lock first!
				print "== Lock relinquished =="
				continue # retry
		# end while - at least one connection has been made
	# end while

# spinoff thread to handle server connections:
# acquire lock
# send OK or BUSY to client
# send map to client
# get updated map from client
# release lock
def serviceThread(cs, addr) :
	global lock, nodeStatus
	
	cs.settimeout(CONNECT_TIMEOUT) # enforce a timeout
	
	try:
		# try to acquire the lock, if it's not available send busy signal to client
		if lock.acquire(0):
			print "== Locked as: Server =="
			
			try:
				# send version signal to client
				cs.send(VERSION)
				cs.recv(len(CLIENT_RPLY))
				
				# before we do anything, update our own status
				updateSelf()
				
				# send status to client
				print "Sending status to client..."
				cs.send(repr(nodeStatus))
				cs.send(EOF)
			
				# receive updated status from client
				print "Receiving updated status from client..."
				tempStatus = receiveStatus(cs)
				if tempStatus == None:
					# we can't be sure whether the client has already updated, and there are simply connection problems, or...?
					# but there's not much we can do about it
					print "Connection error: failed to receive update from client"
				else:
					nodeStatus = tempStatus
					print "Status updated! Writing to XML..."
					xml.dumpToXML(nodeStatus)
			except socket.error, err:
				print err
			
			# relinquish lock
			lock.release()
			print "== Lock relinquished =="
		else:
			cs.send(BUSY_SIGNAL)
	except socket.error, err:
		print err
		
	cs.close()

def main():
	print ""
	print "***********************************"
	print "   Monitoring script initialized   "
	print "***********************************"
	
	# load the nodes into memory
	loadNodes()
	
	# read rev from file if possible 
	try:
		f = open(CLK_FILE, 'r')
		clk = string._int(f.readline())
		f.close()
	except IOError:
		clk = 0 # file does not exist

	print "Setting up 'server' socket to handle inbound connections..."
	
	try:
		ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ss.bind(("", PORT))
		ss.listen(5) # maximum number of waiting nodes is usually 5
	except socket.error, err:
		# either we failed to create the socket or the address is already bound; either way exit
		print err
		sys.exit(1) # exit
		
	print "Server setup complete. Ready to accept connections."
	
	# spawn client thread to periodically 
	print "Spawning 'client' thread to handle outbound connections..."
	thread.start_new_thread(clientThread, ()) # TODO: or should we use main threading module?
	
	while True:
		try:
			# keep spinning off new threads to handle requests
			thread.start_new_thread(serviceThread, tuple(ss.accept()))
		except socket.timeout:
			pass
			
# ***************************************************************
# program begin
# ***************************************************************
main()