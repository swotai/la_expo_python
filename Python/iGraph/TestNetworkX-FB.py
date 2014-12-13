# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 07:36:18 2014

@author: Dennis
"""

import networkx as nx
space = "C:\Users\Dennis\Downloads\css-zipped/"

#### MAIN EXERCISE: Your Facebook ego-network

# Use the following website to download your facebook ego-network data:
# http://apps.facebook.com/netvizz/

# Check all of the boxes in Step 1.  And in Step 2, click the link for the "slow but robust algorithm".

# Check out the file you downloaded. Note the format.

# How will you load all of this into networkx?  My suggestion would be to first create two text files, one with just
# nodes, and another with edges.  Remove the headers from both since it's easy to keep track of what each
# field in each line is telling you.

# Then, create an empty graph.  Load all of the nodes, and then load all of the edges.
# For the node file, I would use the numeric IDs, and store the actual name of the facebook friend
# as node data.

#### Create empty graph
g = nx.Graph()


#### Load all nodes
f = open(space+'fb-nodes.txt', 'r')
l = f.readline()
while (l != ''):
	# add nodes into graph
	row = l.split(',')
	node = int(row[0].strip())
	name = row[1].strip()
	sex  = row[2].strip()
	loc  = row[3].strip()
	ager = int(row[4].strip())
	
	g.add_node(node,name = name, sex = sex, locale = loc, agerank = ager)
	l = f.readline()
f.close()

#### Load all edges
f = open(space+'fb-edges.txt', 'r')
l = f.readline()
while (l != ''):
	row = l.split(',')
	node1 = int(row[0].strip())
	node2 = int(row[1].strip())
	
	g.add_edge(node1, node2)
	l = f.readline()
f.close()


# OUTPUT 1: your facebook friend with the highest degree centrality, the two facebook friends you have
# who have the most friends in common, the number of components in your facebook ego-network, the
# small world coefficient of the largest component in your facebook network (transitivity/diameter)

#### Friend with highest centrality
###### create placeholders, load degree dict
max_degree = 0
friend = ""
fb_dict = nx.degree(g)

###### Loop it through and output
for node in fb_dict:
	if fb_dict[node] > max_degree:
		max_degree = fb_dict[node]
		friend = g.node[node]['name']

print friend, "has the most common friends with you:", max_degree, "in common"


#### Two fb friends with most common friends (with most neighbors)
# ??? CONNECTIVITY??? 

#### Components in the ego network
print "There are", len(nx.connected_components(g)), "connected components in the network"
#### the following prints the subgraphs
# nx.connected_component_subgraphs(g)


### Small world coefficient (transitivity/diameter)
##### Extract the largest subgraph (first one?)
max_size = 0
biggest = -1

for i,component in enumerate(nx.connected_components(g)):
#	print "len:", len(component), "maxsize:", max_size, "i:", i, "biggest:", biggest
	if len(component) > max_size:
		max_size = len(component)
		biggest = i

print "biggest item is" ,biggest
biggest_sub = nx.connected_component_subgraphs(g)[biggest]

smi = nx.transitivity(biggest_sub)/ nx.diameter(biggest_sub)
print "small world index:", smi


# OUTPUT 2: graph the degree distribution using stata, R, etc., or at least output the data that you can 
# use to graph it.  A degree distribution graph is a bar graph with degree on the x-axis and number of nodes
# with that degree on the y-axis.

#### Degree on x, number of node on y
# >> output fb_dict, hist degree
deg_freq = fb_dict.values()
import matplotlib.pyplot as plt

plt.hist(deg_freq,50)
plt.xlabel('Degree')
plt.ylabel('Number of friends')
plt.title('Degree distribution graph of FB friends')


# OUTPUT 3: From this network, create a dataset. The unit of analysis (each row) should be a facebook friend.
# For variables (columns), output the facebook friend's degree centrality, clustering coefficient, eigenvector centrality
# declarative intensity, gender, and wall post counts.

# With this dataset explore some correlations between these features.  How does gender affect centrality?  Do friends in
# more tightly-knit local networks have more activity on facebook?

