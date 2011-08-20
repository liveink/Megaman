#!/usr/bin/env python
#--------------------------------------------------------------------------------
# megaman.py
#
# Solves the megaman problem at http://wiki.dropbox.com/Drew. Written by Rishi
# Ramraj, Aug 14 2011.
#--------------------------------------------------------------------------------

# A linear programming solver.
import pymprog

def solve(map):
	'''
	Solves the problem, given a map as described in http://wiki.dropbox.com/Drew.
	'''
	# First begin by dissecting the map. length holds the total number
	# of blocks and space on the map.
	length = len(map)

	# Edge case.
	if length <= 1:
		return ''

	# Make a rough estimate of the worst case time needed to complete the map.
	# I calculated worst case using maps like x.5x and x.5x.5x. They yielded
	# approximates a traversal time that was twice the number of blocks. To
	# be safe, we'll allocate three times the amount.
	time = 3*length

	# Create the model.
	model = pymprog.model('megaman')

	# The board has axis of blocks and time.
	board = model.var(pymprog.iprod(range(time),range(length)),'Board',bool)

	# Add the constraints from the map.
	addMapConstraints(model,board,map,time)

	# Add the constraints from the baord.
	addBoardConstraints(model,board,length,time)

	# Prefer the shorter solutions.
	model.min(sum(i*board[i,j]/(j+1)
		for i in range(time)
		for j in range(length)))

	# Solve the problem.
	model.solvopt(method='exact', verbosity=2)
	model.solve(int)

	# Print some results.
	for i in range(time):
		for j in range(length):
			print int(board[i,j].primal) ,
		print

def findAllChars(string,char):
	'''
	Returns an indexed list of the occurrences of the given character.
	'''
	# The result of the calculation.
	result = []

	# The location of the next character in the string.
	location = string.find(char)

	# Loop until you can't find another occurrence.
	while location != -1:
		result.append(location)
		location = string.find(char,location+1)

	# Return successfully.
	return result

def addMapConstraints(model,board,map,time):
	'''
	Adds constraints to the board based on the map.
	'''
	# First, analyze the map and produce a dictionary of lists
	# that contain the indices of the respective disappearing
	# blocks.
	blocks = {}
	blocks[0] = findAllChars(map,'.')
	blocks[1] = findAllChars(map,'1')
	blocks[2] = findAllChars(map,'2')
	blocks[3] = findAllChars(map,'3')
	blocks[4] = findAllChars(map,'4')
	blocks[5] = findAllChars(map,'5')

	# Then loop through each set of blocks and create their
	# respective constraints. We want to remove blocks when
	# the current block is '.' (empty space) or when the block
	# is invisible. i has to be incremented below to make
	# sure we're always counting from 1 when modding (otherwise
	# every there'll be an additional time step before things
	# go invisible) and block has to be incremented by one
	# because things stay invisible for the block count and
	# then become visible on the step after.
	for block in blocks:
		model.st([board[i,j] == 0.0
			for j in blocks[block]
			for i in range(time) if (block == 0 or (i+1)%(block+1) != 0)])

		"""
		print block
		print blocks[block]

		for i in range(time):
			for j in range(len(map)):
				if (block == 0 or (i+1)%(block+1) != 0) and j in blocks[block]:
					print 0,
				else:
					print 1,
			print
		print
		"""

def addBoardConstraints(model,board,length,time):
	'''
	Adds constraints to the board based on the rules of the game.
	'''
	# Megaman always starts at the beginning of the board.
   	model.st(board[0,0] == 1)

	# Megaman has to reach the end.
   	model.st(sum(board[i,length-1] for i in range(time)) == 1)

	# There can only be one megaman.
	model.st([sum(board[i,j] for j in range(length)) <= 1 for i in range(time)])

	# Megaman can only jump two blocks. I've hardcoded the jump size here
	# because larger numbers change the logic of the constraints.
	model.st([sum(board[x,y] for x in range(i,i+2) for y in range(j,j+3)) ==
		2*(1-sum(board[z,length-1] for z in range(i)))
		for i in range(time-1)
		for j in range(length-2)])

# Unit tests.
if __name__ == '__main__':
	solve('x.x')

