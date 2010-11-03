#! /usr/bin/env python

import systemScripts
import elementtree.ElementTree as ET

# build a tree structure
root = ET.Element("ClusterStatus")

hostname = ET.SubElement(root, "hostname")
hostname.text = systemScripts.getHostName()

memory = ET.SubElement(root, "memory")
memCap = ET.SubElement(memory, "mem_cap")
memCap.text = systemScripts.getCapacity()
availMem = ET.SubElement(memory, "avail_mem")
availMem.text = systemScripts.getAvailableSpace()
usedMem = ET.SubElement(memory, "used_mem")
usedMem.text = systemScripts.getUsedSpace()

time = ET.SubElement(root, "time")
upTime = ET.SubElement(time, "up_time")
upTime.text = systemScripts.getUptime()
sysTime = ET.SubElement(time, "sys_time")
sysTime.text = systemScripts.getSystemTime()

cpu = ET.SubElement(root, "cpu")
cpuVals = systemScripts.getCpuLoad()
cpu1 = ET.SubElement(cpu, "cpu1")
cpu1.text = cpuVals[0]
cpu5 = ET.SubElement(cpu, "cpu5")
cpu5.text = cpuVals[1]
cpu15 = ET.SubElement(cpu, "cpu15")
cpu15.text = cpuVals[2]

# wrap it in an ElementTree instance, and save as XML
tree = ET.ElementTree(root)
tree.write("page.xhtml")

