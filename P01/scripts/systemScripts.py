#! /usr/bin/env python

import os
import commands

BYTES_IN_MEGABYTE = 1048576
LOAD_AVERAGE_STR = 'load average:' # substring we will use to parse output of 'uptime' command


def getHostName() :
	hostname = commands.getoutput('hostname')
	return hostname

def getCapacity() :
	disk = os.statvfs("/")
	return str((disk.f_bsize * disk.f_blocks) / BYTES_IN_MEGABYTE) + " MB"

def getAvailableSpace() :
	disk = os.statvfs("/")
	# f_bfree returns total # of unused blocks
	# alternatively, use f_bavail for free blocks available to non-superuser
	return str((disk.f_bsize * disk.f_bfree) / BYTES_IN_MEGABYTE) + " MB"

def getUsedSpace() :
	disk = os.statvfs("/")
	return str((disk.f_bsize * (disk.f_blocks - disk.f_bavail)) / BYTES_IN_MEGABYTE) + " MB"

def getSystemTime() :
	s = commands.getoutput('uptime').strip()
	return s[0:s.find(' ')]

def getUptime() :
	s = commands.getoutput('uptime')
	return s[s.find('up') + len('up'):s.find(',')].strip()

def getCpuLoad() :
	s = commands.getoutput('uptime')
	loadAll = s[s.find(LOAD_AVERAGE_STR) + len(LOAD_AVERAGE_STR):len(s)].strip()
	load1 = loadAll[0:loadAll.find(',')].strip()
	load5 = loadAll[len(load1) + 1:loadAll.rfind(',')].strip()
	load15 = loadAll[loadAll.find(load5) + len(load5) + 1:len(loadAll)].strip()
	return [load1, load5, load15]

