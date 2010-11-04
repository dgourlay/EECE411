import os
import stats

# takes two maps and returns a single, combined map containing the most recent entries from each
# note that it operates directly on the map 'mine'
def doUpdate(mine, other) :
	# use local map as a starting point:
	# loop over other map
	# if key doesn't exist in local map, copy it over
	# if key exists, do a comparison & update
	nodes = other.keys()
	for n in nodes :
		if not mine.has_key(n) :
			# the other map has a new key that doesn't exist in the local map; copy it over
			mine.update({n:other[n]})
		else :
			# the key exists in both maps; do a comparison:
			# compare their clk against your own
			# if theirs is higher, update your own entry
			# if they are the same but DEAD_FLAG is on, then update DEAD_FLAG
			# if theirs is lower, update their entry
			m_nodeStatus = mine[n]
			o_nodeStatus = other[n]
			
			m_clk = m_nodeStatus[0]
			o_clk = o_nodeStatus[0]
			
			if m_clk < o_clk : # their clock is higher
				# update the local map entry
				mine.update({n:o_nodeStatus})
			elif m_clk == o_clk : # clock are the same
				m_dead = m_nodeStatus[1]
				o_dead = o_nodeStatus[1]
				 # check dead flag; this is the only value in which the two statuses can differ
				if m_dead != o_dead :
					if m_dead == 1 :
						# update their map entry
						other.update({n:m_nodeStatus})
					if o_dead == 1 :
						# update the local map entry
						mine.update({n:o_nodeStatus})
			else : # local clock is higher
				# update their map entry
				other.update({n:m_nodeStatus})
	# end for

# update map with system status
# note this function operates directly on 'mine'
def updateOwnStatus(mine, clk):
	ownStatus = [clk, 0,
		stats.getCapacity(),
		stats.getAvailableSpace(),
		stats.getUsedSpace(),
		stats.getUptime(),
		stats.getSystemTime(),
		stats.getCpuLoad()]
	mine.update({os.uname()[1]: ownStatus})
	
# set the dead flag for a certain node in the map
# note that this function operates directly on 'mine'
def setDeadFlag(mine, node) :
	if mine.has_key(node):
		s = mine[node]
		s[1] = 1 # set dead flag to true
		mine.update({node:s})
	else:
		mine.update({node:[0, 1, '-', '-', '-', '-', '-', '-']})
	