# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 07:29:13 2014

@author: Dennis
"""

import igraph # You can't execute this code without iGraph
import networkx as nx
from sets import Set
space = "C:\Users\Dennis\Downloads\css-zipped/"

# Exercise 2

g = nx.Graph()

# HINT: Create empty dictionaries to keep track of nodes in a given state, and nodes in a given year
state_dict = {}
year_dict = {}

# HINT: Use a while loop to create network by adding edges AND to keep track of which nodes belong to which
# year and state.
f = open(space+'smo_temp.txt', 'r')

l = f.readline()

while (l != ""):	

	row = l.split('\t')

	# HINT: store the year and state in each line in a variable.

	year = int(row[5])
	state = row[4]

	# HINT: Cycle through each node once with a for loop to assign each node to the state and year dictionaries.

	for smo1 in row[0:4]:
		g.add_node(smo1)
		if state not in state_dict:
			state_dict[state] = Set([])		
		state_dict[state].add(smo1)
		if year not in year_dict:
			year_dict[year] = Set([])
			
		year_dict[year].add(smo1)

		# HINT: add another for loop cycling through each node in the line to get pairs of nodes.

		for smo2 in row[0:4]:
			if smo1 < smo2: # HINT: make sure the first loop's node and the second loop's node are not the same. 
				if (smo1 != "") & (smo2 != ""):  # HINT: Make sure to check that the string in smo1 and smo2 are not blank!
 					g.add_edge(smo1, smo2)

	l = f.readline()

# HINT: use nx.subgraph() command
sub_g_ny = nx.subgraph(g, state_dict['NY'])

print max(nx.degree(g).values())
print nx.transitivity(g)

print max(nx.degree(sub_g_ny).values())
print nx.transitivity(sub_g_ny)

for year in range(1961, 1966):
	sub_g_year = nx.subgraph(g, year_dict[year])
	print "Year: "+str(year)
	print max(nx.degree(sub_g_year).values())
	print nx.transitivity(sub_g_year)