#!/usr/bin/python

import alphafairnesssolver as a
import slicer as sl

#simple network with 3 nodes
# adjacency matrix of the network: if node i is connected to node j, matrix(i, j) is equal to the link capacity, otherwise 0 
matrix = [[0, 100, 100], [100, 0, 10], [100, 10, 0]]
#pair of ports for each link
portMatrix = [[[], [1, 2], [2, 1]], 
			  [[2, 1], [], [1, 2]], 
			  [[1, 2], [2, 1], []]]
#traffic estimates for each demand
trafficMatrix = [[[0, 100, 100], 
	              [100, 0, 100], 
	              [100, 100, 00]], 
	             [[0, 100, 100], 
	              [100, 0, 100], 
	              [100, 100, 00]]]
#creates the problem
s = a.AlphaFairnessSolver(sl.Network(matrix, portMatrix), trafficMatrix, {1:1, 2:2})
#manually adding a demand...
#s.demands[0].addPath([s.network.links[1], s.network.links[2]], s.network)
#solves the problem
s.run()
#show the results
s.showResults()
#manually gettig the path between nodes 1 and 2 (first traffic class 1, then 2)
s.getPathByNodes(1, 2, 1)
s.getPathByNodes(1, 2, 2)
