#!/usr/bin/python

import copy

class PathGenerator(object):

	def __init__(self, matrix):
		'''
		Input: matrix [list of lists of integers]
		'''
		#network adjacency matric, this is the base network to use in all the methods when no other networks are specified
		self.matrix = matrix
		#initial maximum distance used in the Dijkstra algorithm
		self.MAXDIST = 10000

	def findClosestToSource(self, nodeList, dist, node):
		'''
		Input: nodeList [list of integer elements], dist [list of integer or float numbers], node [integer]
		Output: currMin [integer]
		Function: finds the closest node to 'node'
		'''
		currMinDist = dist[0]
		currMin = nodeList[0]
		for n in nodeList:
			if dist[n] < currMinDist:
				currMin = n
		return currMin

	def findNeighbors(self, u, network=None):
		'''
		Input: u [integer], network [list of lists of integer elements]	
		Output: neighbors [list of integers]
		Function: finds the neighbors of 'u' in the 'network' network 
		'''
		if network == None:
			network = copy.deepcopy(self.matrix)
		neighbors = []
		for idx, n in enumerate(network[u]):
			if n > 0:
				neighbors.append(idx)
		return neighbors

	def dijkstra(self, source, network=None):
		'''
		Input: source [integer], network [list of lists of integer elements]
		Output: dist [list of integers], prev [list of integers]
		Function: applies the Dijkstra algorithm to find the distances to each node of the 'network' network from 'source'; moreover 'prev' returns the list of previous node in the considered path
		'''
		if network == None:
			network = copy.deepcopy(self.matrix)
		Q = [i for i in range(len(network))] 
		dist = [self.MAXDIST for i in range(len(network))] 
		prev = ['Undef' for i in range(len(network))] 
		dist[source] = 0

		while Q != []:
			u = self.findClosestToSource(Q, dist, source)
			neighbors = self.findNeighbors(u, network)
			Q.remove(u)

			for n in neighbors:
				alt = dist[u] + network[u][n] #TODO: cost is 1/network[u][n]
				if alt < dist[n]:
					dist[n] = alt
					prev[n] = u  	
		return dist, prev

	def kShortestPath(self, source, destination, K):
		'''
		Input: source [integer], destination [integer], K [integer]
		Output: A [list of lists of integers]
		Function: applies the Yen algorithm to find the k shortest loopless paths betweeen 'source' and 'destination' over the 'self.matrix' network
		'''
		A, B = [], []
		A.append(self.findBestPath(source, destination))
		if not A[0]: return A
		network = copy.deepcopy(self.matrix)
		for k in range(1, K):
			for i in range(0, len(A[-1])-1):
				spurNode = A[-1][i]
				rootPath = A[-1][:i+1]
				for p in A:
					if len(p) > i and rootPath == p[:i+1]:
						network = self.removeEdge(network, p[i], p[i+1])
				#next 'for' loop avoids paths containing loops
				for n in rootPath[:-1]:
					self.removeNode(network, i)
				spurPath = self.findBestPath(spurNode, destination, network)
				if spurPath != []:
					totalPath = rootPath + spurPath[1:]
					B.append(totalPath)
				network = copy.deepcopy(self.matrix)
			if B == []:
				break
			B, costs = self.sortPathsByCost(B)
			A.append(B[0])
			B.pop(0)
		return A

	def removeEdge(self, network, i, j):
		'''
		Input: network [list of lists of integer elements], i [integer], j [integer]
		Output: network [list of lists of integer elements]
		Function: removes the link connecting the nodes 'i' and 'j' from the 'network' network
		'''
		network[i][j] = 0
		network[j][i] = 0
		return network

	def removeNode(self, network, i):
		'''
		Input: network [list of lists of integer elements], i [integer]
		Output: network [list of lists of integer elements]
		Function: removes the links going to and from node 'i' from the 'network' network
		'''
		network[i] = [0]*len(network[i])
		for r in network:
			r[i] = 0
		return network

	def sortPathsByCost(self, paths):
		'''
		Input: paths [list of lists of integer elements]
		Output: ordered [list of lists of integer elements], costs [list of integer elements]
		Function: orders by cost the passed paths and returns the ordered array of paths and its costs
		'''
		#computes costs for each path
		costs = [0 for p in paths]
		for ppx, p in enumerate(paths):
			for ndx  in range(len(p[:-1])):
				linkSource = p[ndx]
				linkDestination = p[ndx + 1]
				costs[ppx] += self.matrix[linkSource][linkDestination]
		#sort paths by costs
		indices = sorted(range(len(costs)), key=lambda k: costs[k])
		ordered = []
		for index in indices:
			ordered.append(paths[index])
		return ordered, sorted(costs)


	def findBestPath(self, source, destination, network=None):
		'''
		Input: source [integer], destination [integer], network [list of lists of integers]
		Output: A [list of lists of integers]
		Function: find the best loopless path betweeen 'source' and 'destination' over the 'network' network based on the output of Dijkstra algorithm
		'''
		if source != destination:
			dist, prev = self.dijkstra(source, network)
			path = [destination]
			curr = prev[destination]
			while curr != source:
				if curr == 'Undef':
					return []
				else:
					path.append(curr)
					curr = prev[curr]
			path.append(source)
			return list(reversed(path))
		else:
			return []


if __name__ == '__main__':

	#example
	# PG = PathGenerator([[0, 1, 0, 0, 10, 0], 
	# 					[0, 0, 1, 20, 5, 0], 
	# 					[0, 0, 0, 1, 0, 0],
	# 					[0, 0, 0, 0, 0, 1],
	# 					[0, 0, 0, 0, 0, 10],
	# 					[0, 0, 0, 0, 0, 0]])
	# dist, prev = PG.dijkstra(0)
	# path = PG.findBestPath(0, 5)
	# print dist
	# print prev
	# print path
	#PG = PathGenerator([[0, 10, 20, 0],
	#					[10, 0, 30, 40],
	#					[20, 30, 0, 60],
	#					[0, 40, 60, 0]])
	#etwork = [[0, 0, 20, 0],
	#		   [0, 0, 30, 40],
	#		   [20, 30, 0, 60],
	#		   [0, 40, 60, 0]]
	PG = PathGenerator([[0, 1.0/100, 1.0/100],
						[1.0/100, 0, 1.0/10],
						[1.0/100, 1.0/10, 0]])
	#A = PG.findBestPath(0, 3)
	#A = PG.findBestPath(0, 3, network)
	#A = PG.dijkstra(0, network)
	A = PG.kShortestPath(0, 2, 2)
	print A