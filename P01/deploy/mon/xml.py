import elementtree.ElementTree as ET

XML_FILE = "/home/usf_ubc_gnutella2/deploy/mon/output/status.xml"

# indices of entry; this should correspond with map.updateOwnStatus()
CLOCK		= 0
DEAD_FLAG 	= 1
CAPACITY 	= 2
AVAIL_SPACE = 3
USED_SPACE 	= 4
UPTIME 		= 5
SYSTIME 	= 6
CPU_LOAD 	= 7

# dump the specified map to an XML file
def dumpToXML(map):
	root = ET.Element("ClusterStatus")
	
	nodes = map.keys()
	for n in nodes:
		# build XML tree
		node = ET.SubElement(root, "node")
		
		nodename = ET.SubElement(node, "name")
		nodeStatus = ET.SubElement(node, "status")
		clock = ET.SubElement(node, "clock")
		
		memory = ET.SubElement(node, "memory")
		memCap = ET.SubElement(memory, "mem_cap")
		availMem = ET.SubElement(memory, "avail_mem")
		usedMem = ET.SubElement(memory, "used_mem")
		
		time = ET.SubElement(node, "time")
		upTime = ET.SubElement(time, "up_time")
		sysTime = ET.SubElement(time, "sys_time")
		
		cpu = ET.SubElement(node, "cpu")
		cpu1 = ET.SubElement(cpu, "cpu1")
		cpu5 = ET.SubElement(cpu, "cpu5")
		cpu15 = ET.SubElement(cpu, "cpu15")
		
		# fill in values from map		
		nodename.text = n
		
		entry = map[n]
		if entry[DEAD_FLAG] == 0:
			nodeStatus.text = "Alive"
			
			clock.text = str(entry[CLOCK])
			
			memCap.text = entry[CAPACITY]
			availMem.text = entry[AVAIL_SPACE]
			usedMem.text = entry[USED_SPACE]
			
			upTime.text = entry[UPTIME]
			sysTime.text = entry[SYSTIME]
			
			cpuVals = entry[CPU_LOAD]	
			cpu1.text = cpuVals[0]
			cpu5.text = cpuVals[1]
			cpu15.text = cpuVals[2]
		else:
			nodeStatus.text = "Dead"
			memCap.text = availMem.text = usedMem.text = upTime.text = sysTime.text = cpu1.text = cpu5.text = cpu15.text = "-"

	# wrap it in an ElementTree instance, and save as XML
	tree = ET.ElementTree(root)
	tree.write(XML_FILE)
	
