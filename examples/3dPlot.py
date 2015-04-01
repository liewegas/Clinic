import math
import os
import sys
import numpy
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import csv
from mpl_toolkits.mplot3d import Axes3D
from numpy import log10

prefix = 'tmp/log.'
outputPrefix = 'figures/'
suffix = ''

# Rows at the beginning of the file while the protocol is still trying to figure out what it should be doing
firstRowsOfJunk = 1500

networkLatencyMeanData = numpy.loadtxt(open(prefix + 'networkLatencyMean' + suffix,'rb'),delimiter='\t',skiprows=firstRowsOfJunk)
networkLatencyVarData = numpy.loadtxt(open(prefix + 'networkLatencyVar' + suffix,'rb'),delimiter='\t',skiprows=firstRowsOfJunk)
clockRandomFreqVarData = numpy.loadtxt(open(prefix + 'clockFreqVar' + suffix,'rb'),delimiter='\t',skiprows=firstRowsOfJunk)

ntpMaxErrorMeanData = numpy.empty(networkLatencyMeanData)

for i in xrange(networkLatencyMeanData.size):
	ntpMaxErrorData = numpy.loadtxt(open(prefix + 'ntp_maxerror' + suffix,'rb'),delimiter='\t',skiprows=firstRowsOfJunk)
	# timeOffsetData = numpy.loadtxt(open(prefix + 'timeoffset' + suffix,'rb'),delimiter='\t',skiprows=firstRowsOfJunk)
	# packetDelayData = numpy.loadtxt(open(prefix + 'packetdelays' + suffix,'rb'),delimiter='\t',skiprows=firstRowsOfJunk)
	# ntpOffsetData = numpy.loadtxt(open(prefix + 'ntp_offset' + suffix,'rb'),delimiter='\t',skiprows=firstRowsOfJunk)
	ntpMaxErrorMeanData[i] = numpy.mean(ntpMaxErrorData)


fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(networkLatencyMeanData, networkLatencyVarData, ntpMaxErrorMeanData, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('Network Latency Mean')
plt.ylabel('Network Latency Variance')
ax.set_zlabel('NTP Max Error Value')
plt.title('NTP Max Error when varying Network Latency')
filename = outputPrefix + 'networkLatencyMean_vs_networkLatencyVariance_vs_MaxError' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename


fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(clockRandomFreqVarData, networkLatencyVarData, ntpMaxErrorMeanData, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('Random Variation in clock frequency')
plt.ylabel('Network Latency Variance')
ax.set_zlabel('NTP Max Error Value')
plt.title('NTP Max Error when varying Network Latency Variance and Clock Frequency Variance')
filename = outputPrefix + 'clockRandomFreqVarData_vs_networkLatencyVariance_vs_MaxError' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename


fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(clockRandomFreqVarData, networkLatencyMeanData, ntpMaxErrorMeanData, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('Random Variation in clock frequency')
plt.ylabel('Network Latency Variance')
ax.set_zlabel('NTP Max Error Value')
plt.title('NTP Max Error when varying Clock Frequency Variance and Network Latency Mean')
filename = outputPrefix + 'clockRandomFreqVarData_vs_networkLatencyMean_vs_MaxError' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename