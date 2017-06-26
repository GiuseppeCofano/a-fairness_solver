#!/usr/bin/python

import alphafairnesssolver as a
import slicer as sl

#more complex network with 6 nodes
# adjacency matrix of the network: if node i is connected to node j, matrix(i, j) is equal to the link capacity, otherwise 0 
matrix = [[0, 30, 10, 0, 0, 0], 
		  [30, 0, 20, 20, 0, 0], 
		  [10, 20, 0, 30, 0, 0],
		  [0, 20, 30, 0, 10, 10],
		  [30, 0, 0, 10, 0, 40],
		  [0, 0, 0, 10, 40, 0]]

trafficMatrix = [[[0, 0, 0, 100, 0, 100], 
		  [0, 0, 0, 0, 0, 100], 
		  [0, 0, 50, 0, 0, 0],
		  [0, 40, 0, 0, 50, 0],
		  [0, 0, 40, 0, 0, 0],
		  [0, 100, 0, 100, 0, 0]],
		  [[0, 0, 0, 100, 0, 100], 
		  [0, 0, 0, 0, 0, 120], 
		  [0, 0, 40, 0, 0, 0],
		  [0, 0, 0, 0, 50, 0],
		  [0, 0, 50, 0, 0, 0],
		  [0, 0, 0, 60, 70, 0]]]

#creates the problem (notices that ports are not passed as an argument)
s = a.AlphaFairnessSolver(sl.Network(matrix), trafficMatrix, {1:1, 2:2})
#solves the problem
s.run()
#show the results
s.showResults()
#how to manually get a path between nodes 1 and 4 (first traffic class 1, then 2)
s.getPathByNodes(1, 4, 1)
s.getPathByNodes(1, 4, 2)