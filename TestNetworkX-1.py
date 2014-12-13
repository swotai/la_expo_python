# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 23:47:27 2014

@author: Dennis
"""
import igraph # You can't execute this code without iGraph
import networkx as nx
space = "C:\Users\Dennis\Downloads\css-zipped/"
###### Solutions to exercises

# Exercise 1

# HINT: Create an empty graph.
g=nx.Graph()


# HINT: Read the edges file using a while loop.
f_edges = open(space+'marvel-edges.txt', 'r')

l = f_edges.readline()

while (l!=""):
	
	# HINT: use split() method to turn each line into a list of elements accessible via an index.
	row = l.split('\t')
	# HINT: assign each node to a variable
	
	node_1 = row[0].strip()
	node_2 = row[1].strip()
	
	# HINT: add edges along with the nodes' data (hero vs. comic)
	g.add_edge(node_1, node_2)
	g.node[node_1]['type'] = 'hero'
	g.node[node_2]['type'] = 'comics'
	
	# HINT: don't forget the read another line from the data file!
	l=f_edges.readline()
	
f_edges.close

# Hero in most comic books
# HINT: create variables to keep track of the maximum degree and the name of hero
max_degree = 0
hero_name = ""

# HINT: create a variable so that you can access the degree dictionary easily
degree_dict = nx.degree(g)

# HINT: use a for loop to run through each node in the degree dictionary...
for node in degree_dict:
	if g.node[node]['type'] == 'hero':
		if degree_dict[node] > max_degree:
			max_degree = degree_dict[node]
			hero_name = node

print "Hero in most comic books:", hero_name, "appeared", max_degree, "times."

# Comic book with most superheroes
max_degree = 0
comic_name = ""
for node in degree_dict:
	if g.node[node]['type'] == 'comics':
		if degree_dict[node] > max_degree:
			max_degree = degree_dict[node]
			comic_name = node

print "Comic with most heros:", comic_name, "with", max_degree, "heros."

# Which superheroes?
# This lists all the heros connected to that comic book in "comic_name"
nx.neighbors(g, comic_name)


# Bipartite projection to hero-to-hero network

# HINT: create empty list object to store those nodes that are heroes in g; use a for loop
# to run through those nodes.
heroes = []
for node in g.nodes():
	if g.node[node]['type'] == 'hero':
		heroes.append(node)


# HINT: see slide
from networkx.algorithms import bipartite
hero_net = bipartite.projected_graph(g, heroes)


# Shortest path
print nx.shortest_path(hero_net, "SPIDER-MAN/PETER PAR", "LITTLE, ABNER")



# Greatest degree centrality
# Which hero is connected to most other heroes???
max_degree = 0
hero_name = ""
degree_dict = nx.degree(hero_net)

for node in degree_dict:
	if g.node[node]['type'] == 'hero':
		if degree_dict[node] > max_degree:
			max_degree = degree_dict[node]
			hero_name = node

print "Hero with highest centrality:", hero_name, "connected", max_degree, "times."


# Neighbors
# This lists who is related to the hero in "hero_name"
nx.neighbors(hero_net, hero_name)


# Connected component sizes

