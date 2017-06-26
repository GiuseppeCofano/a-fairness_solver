#!/usr/bin/python

from cvxpy import * #as cvx
import numpy
from numpy import matlib
from slicer import * 
from basesolver import *

class AlphaFairnessSolver(BaseSolver):

	def __init__(self, network=None, demands=None, tCW=None):
		'''
		Input: network [object of class Network], demands [list of objects of class Demand], tCW [dict]
		'''
		super(AlphaFairnessSolver, self).__init__(network, demands)
		#dictionary linking the traffic class to its weight in the objective function
		self.trafficClassesWeights = tCW
		self.minAcceptRate = 0.001

	def genObjective(self):
		'''
		Function: creates the objective function
		'''
		w_d = self.genDemandWeights()
		#TODO: here alpha fairness should be implemented...
		self.objective = Maximize(w_d.T*log(self.variables['X'])) #.T is the transpose

	def genConstraints(self):
		'''
		Function: generates all constraints
		Explanation:
		1) and 2)  X and x positive slices
		3) sum of the path slices equal to the demand slice
		4) sum of the path slices less than the link capacities
		5) demand slice less than the demand
		'''
		D = self.genDemandArray()
		A_dp = self.genPathToDemandMatrix()
		C, C_dp = self.genPathToCapacityMatrix()
		self.constraints = [0 <= self.variables['X'], 0 <= self.variables['x'], A_dp*self.variables['x'] == self.variables['X'], C_dp*self.variables['x'] <= C, self.variables['X'] <= D]

	def genVariables(self):
		'''
		Function: generates the optimization variables (x -> path slices, X -> demand slices)
		'''
		self.variables['x'] = Variable(self.compPathNumber())
		self.variables['X'] = Variable(len(self.demands))

	def compPathNumber(self):
		'''
		Output: pathNumber [integer]
		Function: computes the total number of paths
		'''
		pathNumber = 0
		for d in self.demands:
			pathNumber += len(d.paths)
		return pathNumber

 	def genDemandArray(self):
 		'''
		Output: D [numpy array]
		Function: generates the array of demand traffic estimates 
		'''
		D = numpy.zeros(len(self.demands))
		for ddx, d in enumerate(self.demands):
			D[ddx] = d.trafficEstim
		return D

	def genPathToDemandMatrix(self):
		'''
		Output: A_dp [numpy matrix]
		Function: generates the matrix (size demands x total paths), where the element (d, p) is equal to 1 if the path p is used by the demand d, 0 otherwise
		'''
		A_dp = numpy.matlib.zeros([len(self.demands), self.compPathNumber()]) 
		position = 0
		for ddx, d in enumerate(self.demands):
			for ppx, p in enumerate(d.paths):
				A_dp[ddx, ppx + position] = 1
			position += len(d.paths) 
		return A_dp   

	def genPathToCapacityMatrix(self):
		'''
		Output: C [numpy array], C_dp [numpy matrix]
		Function: generates the array of link capacities C and and the matrix C_dp (size links x total paths) where each element (l, p) is equal to 1 if the path p passes through the link l, 0 otherwise 
		'''
		C_dp = numpy.matlib.zeros([len(self.network.links), self.compPathNumber()])
		C = numpy.zeros(len(self.network.links)) 
		for ldx, l in enumerate(self.network.links):
			C[ldx] = l.capacity
			position = 0
			for ddx, d in enumerate(self.demands):
				for ppx, p in enumerate(d.paths):
					for lpx, lp in enumerate(p.links):
						if l == lp:
							C_dp[ldx, position + ppx] = 1
				position += len(d.paths)
		return C, C_dp 

	def genDemandWeights(self):	
		'''
		Output: w_d [numpy array]
		Function: generate the array of weights for each demand (the weight corresponds to the traffic class of the demand)
		'''	
		w_d = numpy.zeros(len(self.demands))
		for ddx, d in enumerate(self.demands):
			w_d[ddx] = self.getWeight(d.trafficClass)
		return w_d

	def getWeight(self, trafficClass):
		'''
		Input: trafficClass [integer]
		Output: self.trafficClassesWeights[trafficClass] [integer]
		Function: obtains the weight corresponding to the traffic class
		'''	
		return self.trafficClassesWeights[trafficClass]

	def showResults(self):
		'''
		Function: prints to screen the results of the optimization
		'''	
		counter = 0
		for idx, i in enumerate(self.variables['X'].value):
			print "DEMAND %d        TRAFFIC: %f        ALLOCATED BANDWIDTH: %f" % (self.demands[idx].id, self.demands[idx].trafficEstim, self.demands[idx].bandwidth) 
			for p in self.demands[idx].paths:
				print "--------------> Slice over %s %s: %f" % (p, p.links, p.bandwidth) 
				counter += 1
			print " "
		print "-------------QUEUES TO SET--------------"
		self.network.showNetworkQoS()

	def setBandwidth(self):
		'''
		Function: enforces over the network the rates computed by solving the optimization problem
		'''	
		counter = 0
		for idx, i in enumerate(self.variables['X'].value):
			self.demands[idx].bandwidth = i
			for p in self.demands[idx].paths:
				if self.variables['x'].value[counter] > self.minAcceptRate:
					p.bandwidth = self.variables['x'].value[counter] 
				else:
					p.bandwidth = 0 
				counter += 1
		#sets bandwidth on each queue
		self.setQoS()

	def setQoS(self):
		'''
		Function: enforces over the QoS queues the rates computed by solving the optimization problem
		'''	
		counter = 0
		for d in self.demands:
			for p in d.paths:
				rate =  p.bandwidth
				queues = p.getQueuesByPath()
				for q in queues:
					q.setMinRate(rate) 
					q.setMaxRate(rate)
				counter += 1

