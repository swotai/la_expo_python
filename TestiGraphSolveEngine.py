# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 21:45:27 2014

@author: Dennis
"""

import igraph as ig
import cPickle as pickle
import time, sys
from sets import Set

def pbar(progress, lapsedtime):
	"""
	Progress bar\n
	Input: progress as fraction of 1, lapsed time as time (using time module)
	"""
	if progress == 0:
		progress = 0.0000001
	timeleft = lapsedtime / progress - lapsedtime
	timeleft = timeleft / 3600
	numhash = int(progress*20)
	sys.stdout.write('\r[{0}] {1:.2%}, ETA {2:.6f} hours.'.format('#'*(numhash), progress, timeleft))
	sys.stdout.flush()

def readcsv(infile, indtype, incol, sort, header):
	"""
	Reads CSV using PANDAS\n
	Inputs: infile as path, indtype as dtype with format [('varname','i8')],
	incol is number of col (must be the same number of item as "indtype"),
	sort (specify which column(s) to sort as [0] or [0,1] where number is column number),
	header (Header either None(no header) or True(there is a header))
	"""
	import pandas as pd
	import numpy as np
	if header != None:
		header = 0
	outFTT = pd.read_csv(infile, header = header)
	outFTT.columns = [i for i,col in enumerate(outFTT.columns)]
	outFTT = outFTT.sort(columns=sort)
	outFTT = np.asarray(outFTT.iloc[:,0:incol].values)
	outFTT = np.core.records.fromarrays(outFTT.transpose(), dtype = indtype)
	outFTT = np.asarray(outFTT)
	return outFTT
	
def readspd_to_dict(spdarray):
	"""
	Convert speed read from CSV into dictionary for use\n
	Input: spdarray as array
	Output: <dict type>
	"""
	detspeed = {}
	for idstn in spdarray:
		if idstn[0] in detspeed:
			print "ERROR in readspd: duplicate idstn in speedarray"
		else:
			detspeed[idstn[0]] = idstn[1]
	return detspeed
		

def updatecost(network, edgelist, spddict):
	"""
	Update the cost on all highway edges.\n
	Inputs: network (igraph network), edgelist(list of edges <use edgelist.values()>), 
	spddict(dictionary of speed),\n
	e.g. use readspd_to_dict(readcsv(space+"detspd0.csv", dtype, 2, [0], True))
	"""
	# Update the cost
	# TODO: comeon!!! focus and work!
	updated_count = 0
	for thisedge in edgelist:
		dist = network.es[thisedge]['distance']
		idstn = network.es[thisedge]['id_stn']
		inSpd = spddict[idstn]
		network.es[thisedge]['cost'] = (11.5375 * dist / inSpd + 0.469 * dist)
		network.es[thisedge]['speed1'] = inSpd
		updated_count +=1
	print "number of edges updated:", updated_count


def bi_search(a,x,lo=0, hi=None):
	from bisect import bisect_left
	hi = hi if hi is not None else len(a)
	pos = bisect_left(a,x,lo,hi)
	return (pos if pos!= hi and a[pos] == x else -1)

def solve(network, ori, dest, detlist):
	"""
	Solves the network routing using igraph's implimentation of 
	dijkstra's algorithm on a directed graph.\n
	Inputs: network (igraph network), origin Vertex, dest Vertex/Vertex LIST (sorted, int),
	detector list (take all detectors and put into sorted list),
	edge dict (edge index, edge cost (update per round, test speed), edge idstn\n
	Outputs: cost_from_O (list with length = # of vertices in dest Vertex LIST),
	detlist (list of lists of detectors (1,0) for each OD pair)
	"""
	# use igraph to solve for routes
	print "solving"
	paths_from_O = network.get_shortest_paths(ori, dest, weights='cost', output="epath")
	print "solved"
	# Gen holder list for cost vector	
	cost_from_O = [0] * len(paths_from_O)
	detlist_from_O = [0] * len(paths_from_O)

	# paths contains route from O to all dest TAZ 
	# Outer: loop through all routes
	for j in range(len(paths_from_O)):
		# For each route, extract route info (cost, detector list)
		path = paths_from_O[j]
		totalcost = 0
		route = [0] * len(detlist)
		# Inner: loop through each edge in each route
		count = 0
		for i in range(len(path)):
#			thiscost = network.es[path[i]]['cost']
#			totalcost += thiscost #if thiscost != 0 else 0
			route[count] = 1 if network.es[path[i]]['id_stn'] != 0 else 0
			count +=1
		cost_from_O[j] = totalcost
		detlist_from_O[j] = route[:-1]
#	return cost_from_O, detlist_from_O
	return cost_from_O


if __name__ == '__main__':
	inSpace = "C:/Users/Dennis/Desktop/DATA/igraph/"
	networkpath = inSpace+'LANetworkClean_graphml.txt'
	
	
	# READING
	# Network
	print "reading igraph"
	time0 = time.time()
	LAroad = ig.Graph.Read_GraphML(networkpath)
	time1 = time.time()
	print "igraph read:", time1-time0, "sec."
	
	# TAZ lists
	print "reading vlist"
	f_vlist = open(inSpace+"tazlist_ig_pickle.txt", 'r')
	vlist = pickle.load(f_vlist)
	f_vlist.close()
	
	# hwy edge lists
	print "reading elist"
	f_elist = open(inSpace+"edgelist_ig_pickle.txt", 'r')
	elist = pickle.load(f_elist)
	f_elist.close()
	
	print "reading tazs, tazsD"
	tazs = sorted(vlist.keys())
	tazsD = []
	for i in tazs:
		tazsD.append(vlist[i])
	
	print "creating detslist"
	detslist = sorted(list(Set(elist.values())))

	time0 = time.time()
	a = solve(LAroad, vlist[20211000], tazsD, detslist)
	time1 = time.time()
	totalhour = (time1 - time0)
	print "Takes a lot of sec:", totalhour
	
	time0 = time.time()
	b = LAroad.shortest_paths(vlist[20211000], weights='cost')
	time1 = time.time()
	totalhour = (time1 - time0)
	print "Takes a lot of sec:", totalhour
	
	
	
	# HINT: How to loop:
	print "igraph solve time:"
	time0 = time.time()
	count = 0
	cost=[0]*len(tazs)
	det=[0]*len(tazs)
	for i in tazs[0:2]:
		costi, deti = solve(LAroad, vlist[i], tazsD, detslist)
		cost[count] = costi
		det[count] = deti
		timec = time.time()
		ltime = timec-time0
		count +=1
		if count > 10:
			break
		progress = count/len(tazs)
		pbar(progress,ltime)
	
	time1 = time.time()
	totalhour = (time1 - time0)/(60*60)
	print "Takes a lot of hours:", totalhour
	
	time0 = time.time()
	a = solve(LAroad, vlist[20211000], tazsD, detslist)
	time1 = time.time()
	totalhour = (time1 - time0)
	print "Takes a lot of sec:", totalhour


if __name__ == '__man__':
		
		
	path1 = LAroad.get_shortest_paths(vlist[22415000], vlist[22018000], weights='cost', output="epath")[0]
	
	destlist = [vlist[22018000],vlist[21199000]]
	path2 = LAroad.get_shortest_paths(vlist[22415000], destlist, weights='cost', output="epath")
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

	# READING SPEED CSV INTO DICT
	test = readspd_to_dict(readcsv(space+"detspd0.csv", dtype, 2, [0], True))
	
	# Read TT flow
	print "importing various matrices"
	#Read TAZ-TAZ flow
	inFlow = inSpace + "CSV/TTflow" + str(currentIter) + ".csv"
	
	fdtype = [('oid','i8'),('did','i8'),('postflow','f8')]
	ff = readcsv(inFlow, fdtype, incol = 3, sort = [0,1], header = None)
	
	def create_elistD(network):
		import time
		print "creating elistD"
		elistD = [0] * len(LAroad.es)
		time0 = time.time()
		ecount = 0
		for edgeid in range(len(LAroad.es)):
#			elistD[edge.index] = (edge['cost'], edge['id_stn'])
			elistD = (LAroad.es[edgeid]['cost'], LAroad.es[edgeid]['id_stn'])
			ecount +=1
		print ecount, "edge enumerated"
		time1 = time.time()
		totalhour = (time1 - time0)
		print "takes", totalhour, "seconds"
		return elistD


	test = create_elistD(LAroad)

