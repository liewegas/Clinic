#!/usr/bin/env python2.7

import math
import os
import sys
import numpy
import scipy
import matplotlib
# import multiprocessing.dummy
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import itertools
import csv
from mpl_toolkits.mplot3d import Axes3D
from numpy import log10


# Rows at the beginning of the file while the protocol is still trying to figure out what it should be doing
firstRowsOfJunk = 1500
# Number of computed parameters to produce. Keep this up to date with processFolder
dimensionsOfComputedData = 9
computedColNames = []
computedColNames += ["Mean of NTP Max Error (ns)", "Max of NTP Max Error (ns)", "STD of NTP Max Error (ns)"]
computedColNames += ["Mean of NTP Freq Offset (ppm??)", "Max of NTP Freq Offset (ppm??)", "STD of NTP Freq Offset (ppm??)"]
# computedColNames += ["Mean of NTP Packet Delays (ms)", "Max of NTP Packet Delays (ms)", "STD of NTP Packet Delays (ms)"]
computedColNames += ["Mean of Absolute Time Offset (s)", "Max of Absolute Time Offset (s)", "STD of Absolute Time Offset (s)"]

def loadFile(fd, cols=(1,)):
	""" returns a single double that results from applying 
		reductionFunc to the array found at path.
		Selects cols from the file at path, by default col 1 (the second col) """

	fileData = numpy.loadtxt(
		fd,
		delimiter='\t',
		skiprows=firstRowsOfJunk,
		usecols = cols)

	return fileData


def processFolder(rootpath, folder, dataArray, index):
	""" path: str, dataArray: numpy array of the necessary order to hold data 
		Currently requires 12 more dimensions than the number of parameters"""

	path = os.path.join(rootpath, folder)
	
	# split the parameters and place them at the relevant index in the matrix
	params = folder.split('_')
	paramsCount = len(params)
	for i in xrange(paramsCount):
		dataArray[index][i] = float(params[i])


	with open(os.path.join(path, "log.ntp_maxerror")) as fd:
		data = loadFile(fd)
		dataArray[index][paramsCount+0] = numpy.mean(data)
		dataArray[index][paramsCount+1] = numpy.amax(data)
		dataArray[index][paramsCount+2] = numpy.std(data)

	with open(os.path.join(path, "log.ntp_offset")) as fd:
		data = loadFile(fd)
		dataArray[index][paramsCount+3] = numpy.mean(data)
		dataArray[index][paramsCount+4] = numpy.amax(data)
		dataArray[index][paramsCount+5] = numpy.std(data)

	# dataArray[index][paramsCount+6] = processFile(os.path.join(path, "log.packetdelays"), numpy.mean)
	# dataArray[index][paramsCount+7] = processFile(os.path.join(path, "log.packetdelays"), numpy.amax)
	# dataArray[index][paramsCount+8] = processFile(os.path.join(path, "log.packetdelays"), numpy.std)

	with open(os.path.join(path, "log.timeoffset")) as fd:
		data = loadFile(fd)
		dataArray[index][paramsCount+6] = numpy.mean(data)
		dataArray[index][paramsCount+7] = numpy.amax(data)
		dataArray[index][paramsCount+8] = numpy.std(data)

	if (index % 100 == 0):
		print "Processed folder %s" % index

def make3dPlot(dataArray, cols, colNames, captionText, pathRoot):
	""" expects a 3-ple of cols """

	fig = plt.figure()
	ax = fig.gca(projection='3d')
	ax.view_init(elev=13, azim=-30)

	x = dataArray[:,cols[0]]
	y = dataArray[:,cols[1]]
	z = dataArray[:,cols[2]]

	surf = ax.plot_trisurf(x, y, z, cmap=cm.jet, linewidth=0.2)

	plt.xlabel(colNames[cols[0]])
	plt.ylabel(colNames[cols[1]])
	ax.set_zlabel(colNames[cols[2]])

	strippedNames = map(lambda x: x.split('(')[0].strip(), [colNames[cols[2]], colNames[cols[1]], colNames[cols[0]]])

	plt.suptitle("{} vs {} vs {}".format(*strippedNames))
	plt.figtext(.1, .8, captionText, verticalalignment=u'baseline', size=u'x-small')
	filename = "{}_{}_{}.svg".format(*strippedNames)
	plt.savefig(os.path.join(pathRoot, filename))
	plt.close()
	print 'saved file to %s' % filename


def getFolderName(path):
	""" try to get name of folder at end of folder path """
	split = os.path.split(path)
	if (split[1] == ""):
		return os.path.split(split[0])[1]
	else:
		return split[1]

def main(rootpath, captionPath, outPath, paramNamesList):

	# calculate where to put the graphs
	
	outputDir = os.path.join(outPath, getFolderName(rootpath))
	if (not os.path.isdir(outputDir)): 
		os.mkdir(outputDir)

	# grab the caption text
	with open(captionPath) as f:
		captionText = f.read()

	rootdir = os.listdir(rootpath)
	dirs = filter(lambda fldr: os.path.isdir(os.path.join(rootpath, fldr)), rootdir)

	dataArray = numpy.empty((len(dirs), len(paramNamesList) + dimensionsOfComputedData))

	# fill out the array with the data in folders
	map(lambda index: processFolder(rootpath, dirs[index], dataArray, index), range(len(dirs)))

	# make the graphs
	numberOfInputParams = len(paramNamesList)
	allParams = paramNamesList + computedColNames
	# pairs of input parameters
	combinationsOfInputParams = [item for item in itertools.combinations(xrange(numberOfInputParams), 2)]
	for outputCol in range(numberOfInputParams, dimensionsOfComputedData + numberOfInputParams):
		for inputComb in combinationsOfInputParams:
			make3dPlot(dataArray, inputComb+(outputCol,), allParams, captionText, outputDir)



if __name__=="__main__":
	if (len(sys.argv) < 4):
		print "Please run with"
		print "\t 1. a directory argument containing the relevant directory structure"
		print "\t 2. a file that contains a text caption to be appended to graphs"
		print "\t 3. a directory path where figures should be saved"
		print "\t 4. axis labels for simulation parameters"
		print
		print 'Example: 3dPlot.py ./data ./caption_text ./figures "param1 (feet)" "param2 (s)" ... "paramN (k)"'
	else:
		main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])