from cvxpy import * #as cvx
import numpy
from numpy import matlib
import copy
import slicer 
from pathgenerator import *

class BaseSolver(object):

	def __init__(self, network=None, trafficMatrix=None):
		'''
		Input: network [object of class Network], trafficMatrix [list of lists of lists of integers]
		'''
		#add a network
		self.network = network
		#generate cost matrix as the inverse of the link bandwidth
		self.costMatrix = self.adjToCosts(self.network.adjMatrix)
		#creates the object used to generate the paths over the network
		self.pathgenerator = PathGenerator(self.costMatrix)
		#creates the demands given the traffic matrix (inside this function the paths are generated)
		self.pathNumber = 2
		self.demands = self.buildDemandsFromTrafficMatrix(trafficMatrix)
		#variables for the optimization problem
		self.objective = None
		self.constraints = []
		self.variables = dict()

	def addDemand(self, d):
		'''
		Input: d [object of class Demand]
		Function: appends the demand to the list of demands to consider in the optimization
		'''
		self.demands.append(d)

	def delDemand(self, id):
		'''
		Input: id [integer]
		Function: deletes a demand by its id
		'''
		d = self.getDemandById(id)
		self.demands.remove(d)

	def getDemandById(self, id):
		'''
		Input: id [integer]
		Output: d [object of class Demand]
		Function: obtains a demand by its id
		'''
		for d in self.demands:
			if d.id == id:
				return d

	def adjToCosts(self, matrix):
		'''
		Input: matrix [list of lists of integers]
		Output: costs [list of lists of floats]
		Function: creates the matrix of link costs given their capacities. The inversion is useful when the link costs is computed from the link capacity, like in this tool. As decreasing function 1/c is employed, like in several industrial solutions. 
		'''
		costs = copy.deepcopy(matrix)
		for rdx, r in enumerate(costs):
			for ndx, n in enumerate(r):
				if n != 0:
					costs[rdx][ndx] = 1.0/n
		return costs

	def buildDemandsFromTrafficMatrix(self, matrix):
		'''
		Input: matrix [list of lists of lists of integers]
		Output: demands [list of objects of class Demand]
		Function: builds the list of demands based on the traffic estimates for each pair of nodes (source, destination). A number of paths equal to self.pathNumber is generated for each demand. 
		'''
		demands = []
		trafficClasses = matrix
		counter = 1
		print "-----------------GENERATING PATHS...---------------------"
		for cdx, c in enumerate(trafficClasses):
			rows = c
			for rdx, r in enumerate(rows):
				#rdx corresponds to the source node id
				elements = r
				for edx, e in enumerate(elements):
					#edx corresponds to the destination node id
					if e > 0:
						demands.append(slicer.Demand(counter, cdx+1, e, rdx+1, edx+1, [], self.network))
						#path = self.pathgenerator.findBestPath(rdx, edx)
						paths = self.pathgenerator.kShortestPath(rdx, edx, self.pathNumber)
						for path in paths:
							pathLinks = []
							for ndx, n in enumerate(path):
								if n == path[-1]:
									pass
								else:
									pathLinks.append(self.network.findLinkBySwitches(n+1, path[ndx+1]+1))
							print "Adding Path " + str(pathLinks) + " for Traffic Class " + str(cdx+1)
							demands[-1].addPath(pathLinks, self.network)
						counter += 1

		print "----------------Path Generation completed-----------------"
		print " "
		return demands

	def genObjective(self):
		'''
		Function: to implement in the derived classes specifiying the optimization problem
		'''
		pass

	def genConstraints(self):
		'''
		Function: to implement in the derived classes specifiying the optimization problem
		'''
		pass

	def genVariables(self):
		'''
		Function: to implement in the derived classes specifiying the optimization problem
		'''
		pass

	def setBandwidth(self):
		'''
		Function: to implement in the derived classes specifiying the optimization problem
		'''
		pass

	def setQoS(self):
		'''
		Function: to implement in the derived classes specifiying the optimization problem
		'''
		pass

	def getPathByNodes(self, src, dst, tC):
		'''
		Input: src [integer], dst [integer], tC [integer]
		Output: output [list of dicts]
		Function: builds the list of dictionaries containing the (switch, port, queue) through which a flow has to go to follow the path decided by the optimization
		'''
		#nodes start from 1 in this context (and not from 0!)...
		for d in self.demands:
			if d.src == src and d.dst == dst and d.trafficClass == tC:
				#this function extracts a unique path from the pool of available paths for the demand
				path = self.getUniquePath(d)
				output = []
				for l in path.links:
					for q in l.QoS:
						if q.path == path:
							queue = q.id
					output.append({'Switch': l.sw1, 'Port': l.port1, 'Queue': queue}) 
				print output
				return output

	def getUniquePath(self, d):
		'''
		Input: d [object of class Demand]
		Output: p [object of class Path]
		Function: extracts a unique path from the pool of available paths for the demand 'd'. The probability with which a path is assigned is proportional to the ratio between path bandwidth and total demand bandwidth 
		'''
		counter = 0
		rnd = numpy.random.uniform(0, d.bandwidth)
		for p in d.paths:
			if rnd < (p.bandwidth + counter):
				return p
			counter += p.bandwidth

	def run(self):
		'''
		Function: builds and solve the optimization problem. Main function to call in order to solve an optimization problem
		'''
		#create the problem by generating constraints and objective functions
		self.genVariables()
		self.genObjective()
		self.genConstraints()
		prob = Problem(self.objective, self.constraints)
		#solve the optimization problem
		prob.solve()
		#populates the .bandwidth attributes in the Path and Demand classes where the results of the optimization are stored
		self.setBandwidth()



		




