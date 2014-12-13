# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 13:13:41 2014

@author: Dennis
"""
import matplotlib.pyplot as plt
import networkx as nx
#G=nx.Graph()
#G.add_node("spam")
#G.add_edge(1,2)
#print(G.nodes())
#
#print(G.edges())
#
## Get edge attributes
#b = nx.get_edge_attributes(A, 'id_stn')
#
## extract all values
#c=b.values()
#

inSpace = "C:/Users/Dennis/Desktop/DATA/"

print "importing"
A = nx.read_shp(inSpace+'LANetworkClean.shp')

count = 0
problem = 9999999999
checkcomplete = []
newG = nx.DiGraph()
print "Converting"
for o, d, attr in A.edges_iter(data=True):
#	print "o:",o,"d:",d	
#	if count > 10000: 
#		break
	count +=1
	# read the attributes to keep:
	fidtiger = attr['FID_TIGER_']
	ftcost = attr['FT_cost']
	idtaz12a = attr['ID_TAZ12A']
	objectid1 = attr['OBJECTID_1']
	oneway = attr['Oneway']
	tfcost = attr['TF_cost']
	cost = attr['cost']
	dist = attr['distance']
	dps = attr['dps']
	hwy = attr['hwy']
	idstn = attr['id_stn']
	speed = attr['speed']
	speed1 = attr['speed1']
	serial = attr['serial']
#	Fullname and LinearID has too many empty entries that crashes.  not worth keeping
#	fullname = attr['FULLNAME']
#	linearid = attr['LINEARID']
	
	# Check which edge has issue	
	var = [fidtiger, ftcost, idtaz12a, objectid1, oneway, tfcost, cost, dist, dps, hwy, idstn, speed, speed1, serial]
	for x in var:
		if x == None:
			print x
			problem = count

	parking = 0
	checkcomplete.append(serial)
	# Create matching edges keeping above attributes:
	newG.add_edge(o,d, 
			FID_TIGER_ = fidtiger,
			FT_cost = ftcost,
#			FULLNAME = fullname,
#			LINEARID = linearid,
			OBJECTID_1 = objectid1,
			Oneway = oneway,
			TF_cost = tfcost,
			cost = cost,
			distance = dist,
			dps = dps,
			hwy = hwy,
			id_stn = idstn,
			speed = speed,
			speed1 = speed1,
			parking = parking)
	# Create opposite edge of digraph if bidirectional (oneway == B)
	if idtaz12a > 0:
		if cost != 0:
			print "edge:", o, d, "tazconn but nonzero cost"
	if tfcost == 10:
		parking = 1
		cost = 10
	if oneway == 'B':
		newG.add_edge(d,o, 
			FID_TIGER_ = fidtiger,
			FT_cost = tfcost,
#			FULLNAME = fullname,
#			LINEARID = linearid,
			OBJECTID_1 = objectid1,
			Oneway = oneway,
			TF_cost = ftcost,
			cost = cost,
			distance = dist,
			dps = dps,
			hwy = hwy,
			id_stn = idstn,
			speed = speed,
			speed1 = speed1,
			parking = parking)

	# HINT: IF TAZ, THEN NO COST TRAVELLING ON THAT LENGTH (TAZCONNS)
			



print "Node attributes"
# Add node attributes: ID_TAZ12A,
# Also records the id and corresponding node into JSON file type.
tazlist = {}
for node in newG.node:
	newG.node[node]['ID_TAZ12A'] = 0
for o,d,attr in A.edges_iter(data=True):
	if attr['ID_TAZ12A'] !=0:
		if attr['ID_TAZ12A'] in tazlist:
			print "Oh No.! Duplicate TAZ!"
		newG.node[o]['ID_TAZ12A'] = attr['ID_TAZ12A']
		tazlist[attr['ID_TAZ12A']] = o

# Save GraphML file
print 'Saving LANetworkClean into graphML'
nx.write_graphml(newG, inSpace+'igraph/LANetworkClean_graphml.txt')

# Save TAZlist raw base on nodes to file TAZlist_json
import cPickle as pickle


# Keeping only TAZs in current TAZ list (to keep consistency) and save to file
TAZ = nx.read_shp(inSpace+'TAZ_LA_proj_centroid.shp')
count = 0
tazlistC = {}
for node in TAZ.node:
	if TAZ.node[node]['ID_TAZ12A'] in tazlist:
		print TAZ.node[node]['ID_TAZ12A'], "in current TAZ list"
		tazlistC[TAZ.node[node]['ID_TAZ12A']] = tazlist[TAZ.node[node]['ID_TAZ12A']]
		count +=1
print count

# TAZs currently in arcGIS version
f=open(inSpace+'igraph/tazlist_nx_pickle.txt', 'wb')
#f.write(json.dumps(tazlistC, sort_keys = True))
pickle.dump(tazlistC,f)
f.close()


# HINT: IMPORTANT: TEST ROUTING IS ALRIGHT
# USE NETWORKX Dijkstra algo for now
#path = nx.dijkstra_path(newG, tazlistC[22415000], tazlistC[22018000], weight = 'cost')
#
## extract edges
#totalcost = 0
#hwyroute = []
#for i in range(1, len(path)):
#	thisedge = newG.edge[path[i-1]][path[i]]
#	totalcost += thisedge['cost']
#	if thisedge['id_stn'] > 0:
#		hwyroute.append(thisedge['id_stn'])
#
#print "total cost:", totalcost
#print "hwy stations:", hwyroute
#
#import cPickle as pickle
#f=open(inSpace+"igraph/tazlist_pickle.txt", 'wb')
#pickle.dump(tazlistC, f)
#f.close()
#
#tazpath = inSpace+'igraph/tazlist_pickle.txt'
#f_taz = open(tazpath, 'r')
#taz = pickle.load(f_taz)
#f_taz.close()


#print "edgecounts"
#edgecount = 0
#for node in newG.edge:
#	for attr in newG.edge[node]:
#		if newG.edge[node]=={}:
#			edgecount+=1
#print edgecount
#
#print "nodecounts"
#nodecount = 0
#for node in newG.node:
#	for attr in newG.node[node]:
#		if newG.node[node]=={}:
#			nodecount+=1
#print nodecount
#
##print "writing edge for check to checkedge.csv"
##f = open(inSpace+'checkedge.csv', 'wb')
##
##for edge in checkcomplete:
##	print>>f, edge
##
##f.close()
#
#print "problem at:", problem



# HINT: NEED TRANSLATION BETWEEN ID_STN at edge and id matrix.


#print newG.edge[(6524607.969692208, 2070721.511719747)][(6524607.734128391, 2070806.9511814106)]
#print newG.edge[(6405917.215276313, 1916526.5891390687)][(6404597.108336463, 1916543.213121553)]



if __name__ == "__man":
	# Check connectivity: any orphaned nodes?
	g=A.to_undirected()
	
	discnodes = []
	# Extract all points in the disconnected subgraphs
	for i, component in enumerate(nx.connected_components(g)[1:]):
		for j, comps in enumerate(component):
			discnodes.append(comps)
	
	from sets import Set
	discnodes = Set(discnodes)
	c=list(discnodes)
	
	f = open(inSpace+'disconnect.csv', 'wb')
	
	for item in c:
		print>>f, item
	
	f.close()
#	Alright.  Only edges have orphaned nodes (because of chopping)
	
#	 Test routing
	
	testdict = nx.degree(nx.connected_component_subgraphs(g)[-1])
	
	
	A.edge[(6536976.468577226, 1751699.982113124)][(6537387.747938392, 1750845.1508175563)]
	A.edge[(6536976.468577226, 1751699.982113124)][(6537387.747938392, 1750845.1508175563)]
	
	# Probably need to write a script to make the conversion:
	# 1, Remove Json, Wkb, Wkt attributes 
	# 2, If Oneway == B, Generate reverse direction edge
	
	## Test:
	
	G = nx.DiGraph()
	
	G.add_edge(1,2, oneway='B', var2="REMOVEREMOVEREMOVE")
	G.add_edge(2,3, oneway='T', var2="REMOVEREMOVEREMOVE")
	G.add_edge(4,2, oneway='B', var2="REMOVEREMOVEREMOVE")
	G.add_edge(4,5, oneway='B', var2="REMOVEREMOVEREMOVE")
	G.add_edge(3,4, oneway='T', var2="REMOVEREMOVEREMOVE")
	
	nx.draw(G)
	nx.write_graphml(G, inSpace+'LANetworkClean_graphml.txt')
	
	for u,v,a in G.edges_iter(data=True):
		print u,v,a['onway']
		
	#Attributes to keep:
	#	FID_TIGER_
	#	FT_cost
	#	FULLNAME
	#	ID_TAZ12A? >> nodes?
	#	LINEARID
	#	OBJECTID_1
	#	Oneway
	#	TF_cost
	#	cost
	#	distance
	#	dps
	#	hwy
	#	id_stn
	#	speed
	#	speed1
		
if __name__ == "debug":
	# debug nonetype?
	# NONETYPE ERROR BECAUSE NODES HAS NO ATTRIBUTES AT ALL.
	# SOLUTION: ADD TAZ ID AS ZERO OR THE ACTUAL TAZ12A NUMBER


	# HINT: NEED TRANSLATION BETWEEN ID_TAZ12A and NODE
	#B = nx.read_shp(inSpace+'TAZ_LA_proj_centroid.shp')
	# debug TAZ: Read taz does not exactly match node coordinates
	# Solution: use node coordinates for TAZ.  More bigger at 27xx but should be ok.
	
	for node in B.node:
		print newG.node[node]
	
	for node in B.node:
		B.node[node]['test'] = 10
	
	taz = 0
	tazlist = {}
	for o, d, attr in A.edges_iter(data=True):
		fidtiger = attr['FID_TIGER_']
		ftcost = attr['FT_cost']
		fullname = attr['FULLNAME']
		idtaz12a = attr['ID_TAZ12A']
		linearid = attr['LINEARID']
		objectid1 = attr['OBJECTID_1']
		oneway = attr['Oneway']
		tfcost = attr['TF_cost']
		cost = attr['cost']
		dist = attr['distance']
		dps = attr['dps']
		hwy = attr['hwy']
		idstn = attr['id_stn']
		speed = attr['speed']
		speed1 = attr['speed1']
		parking = 0
	
		if idtaz12a !=0:
	#		print "o", o, "id:", idtaz12a
			taz+=1
			tazlist[idtaz12a]=o
	print taz
	
	B.node[(6406289.303770974, 1923122.8246342242)]
	tazlist[20660000]
		