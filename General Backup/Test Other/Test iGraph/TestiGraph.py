# -*- coding: utf-8 -*-
"""
Created on Mon Nov 03 21:29:55 2014

@author: Dennis
"""




#f=open(inSpace+"tazlist_index_pickle.txt", 'wb')
#pickle.dump(vlist, f)
#f.close()

import igraph as ig
import cPickle as pickle
import networkx as nx
import time, sys

def pbar(progress, lapsedtime):
	if progress == 0:
		progress = 0.0000001
	timeleft = lapsedtime / progress - lapsedtime
	timeleft = timeleft / 3600
	numhash = int(progress*20)
	sys.stdout.write('\r[{0}] {1:.2%}, ETA {2:.6f} hours.'.format('#'*(numhash), progress, timeleft))
	sys.stdout.flush()

	
inSpace = "C:/Users/Dennis/Desktop/DATA/igraph/"
networkpath = inSpace+'LANetworkClean_graphml.txt'


time0 = time.time()
LAroad = ig.Graph.Read_GraphML(networkpath)
time1 = time.time()
print "igraph read:", time1-time0, "sec."


time0 = time.time()
LAroadx = nx.read_graphml(networkpath)
time1 = time.time()
print "NetworkX read:", time1-time0, "sec."

f_taz = open(inSpace+'tazlist_nx_pickle.txt', 'r')
taz = pickle.load(f_taz)
f_taz.close()

f_vlist = open(inSpace+"tazlist_ig_pickle.txt", 'r')
vlist = pickle.load(f_vlist)
f_vlist.close()



#TEST PASSED.  
from sets import Set

path = nx.dijkstra_path(LAroadx, str(taz[22415000]), str(taz[22018000]), weight = 'cost')
# extract edges
totalcost = 0
hwyroute = []
for i in range(1, len(path)):
	thisedge = LAroadx.edge[path[i-1]][path[i]]
	totalcost += thisedge['cost']
	if thisedge['id_stn'] > 0:
		hwyroute.append(int(thisedge['id_stn']))
hwyroute=list(Set(hwyroute))
print "total cost:", totalcost
print "hwy stations:", hwyroute


path1 = LAroad.get_shortest_paths(vlist[22415000], vlist[22018000], weights='cost', output="epath")[0]
# extract edges
totalcost_ig = 0
hwyroute_ig = []
for i in range(1, len(path1)):
	thisedge = LAroad.es[path1[i]]
	totalcost_ig += thisedge['cost']
	if thisedge['id_stn'] > 0:
		hwyroute_ig.append(int(thisedge['id_stn']))
hwyroute_ig=list(Set(hwyroute_ig))
print "total cost:", totalcost_ig
print "hwy stations:", hwyroute_ig



## PARALLEL CODE


#from joblib import Parallel, delayed
#import multiprocessing
#
#num_cores = int(multiprocessing.cpu_count()*.75)
#
#def getpath(i,j):
#	count +=1
#	x = LAroad.get_all_shortest_paths(LAroad.vs.find(ID_TAZ12A=i).index, 
#				LAroad.vs.find(ID_TAZ12A=j).index, 
#				weights='cost')
#	timec = time.time()
#	ltime = timec-time0
#	progress = count/totalsize
#	pbar(progress,ltime)
#	return x
#
#


#
#
#print "NetworkX solve time:"
#time0 = time.time()
#count = 0.0
#for i in alist:
#	for j in alist:
#		count +=1
#		x = nx.dijkstra_path(LAroadx, taz[i], taz[j], weight = 'cost')
#		timec = time.time()
#		ltime = timec-time0
#		progress = count/totalsize
#		pbar(progress,ltime)
#
#time1 = time.time()
#totalhour = (time1 - time0)/(60*60)
#print "Takes a lot of hours:", totalhour
#
#del LAroadx


#
#
#time0 = time.time()
#for i in range(10):
#	time.sleep(0.1)
#	timec=time.time()
#	ltime = timec-time0
#	pbar(float(i)/10, ltime)

# Save tutorial materials




# OTHER CODE
#


#
#
#
#print "igraph solve time for one TAZ to all other TAZ:"
#time0 = time.time()
#x = LAroad.get_shortest_paths(0, vlist, weights='cost')
#time1 = time.time()
#totalhour = (time1 - time0)/(60*60)
#print "Takes a lot of hours:", totalhour
#
#
#print "igraph solve time:"
#time0 = time.time()
#count = 0.0
#for i in vlist:
#	count +=1
#	x = LAroad.get_all_shortest_paths(i, 
#				vlist, weights='cost')
#	timec = time.time()
#	ltime = timec-time0
#	progress = count/totalsize
#	pbar(progress,ltime)
#
#time1 = time.time()
#totalhour = (time1 - time0)/(60*60)
#print "Takes a lot of hours:", totalhour






##### Setup: 
##### TAZlist with TAZNUM: Vertex ID
##### Edgelist with EdgeID: id_stn
# REQUIRE TAZLIST loaded as taz
#alist = taz.keys()
#totalsize = len(alist)
#vlist = {}
#for node in alist:
#	vlist[node] = LAroad.vs.find(ID_TAZ12A=node).index
#
#f=open(inSpace+"tazlist_ig_pickle.txt", 'wb')
#pickle.dump(vlist, f)
#f.close()
#
#elist = {}
#edgelist = LAroad.es.select(id_stn_ne=0)
#for edge in edgelist:
#	elist[edge.index] = int(edge['id_stn'])
#print len(elist)
#
#f=open(inSpace+"edgelist_ig_pickle.txt", 'wb')
#pickle.dump(elist, f)
#f.close()

#f_vlist = open(inSpace+"tazlist_ig_pickle.txt", 'r')
#vlist = pickle.load(f_vlist)
#f_vlist.close()












if __name__ == '__man':
	import igraph as ig
	
	
	g = ig.Graph([(0,1), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3), (5,6)])
	
	print g.vs
	g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
	g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
	g.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
	g.es["is_formal"] = [False, False, True, True, True, False, True, False, False]
	
	# g.vs (vertice/node) and g.es (edge) are dictionary
	
	
	print g.vs.select(age_eq=22)['name']
	
	layout = g.layout("kk")
	ig.plot(g, layout = layout)
	
	g.vs["label"] = g.vs["name"]
	color_dict = {"m": "blue", "f": "red"}
	g.vs["color"] = [color_dict[gender] for gender in g.vs["gender"]]
	ig.plot(g, layout = layout, bbox = (300, 300), margin = 20)