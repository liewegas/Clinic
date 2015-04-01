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

prefix = 'data/'
outputPrefix = 'figures/'
suffix = '_shuffler'

numberOfObjectsData = numpy.loadtxt(open(prefix + 'numberOfObjects' + suffix + '.csv','rb'),delimiter=',',skiprows=0)
numberOfNeighborsData = numpy.loadtxt(open(prefix + 'numberOfNeighbors' + suffix + '.csv','rb'),delimiter=',',skiprows=0)

staticVectorData = numpy.loadtxt(open(prefix + 'StaticPoint_Vector_Times' + suffix + '.csv','rb'),delimiter=',',skiprows=0)
dynamicVectorData = numpy.loadtxt(open(prefix + 'DynamicPoint_Vector_Times' + suffix + '.csv','rb'),delimiter=',',skiprows=0)
arrayOfPointersVectorData = numpy.loadtxt(open(prefix + 'ArrayOfPointersPoint_Vector_Times' + suffix + '.csv','rb'),delimiter=',',skiprows=0)
listVectorData = numpy.loadtxt(open(prefix + 'ListPoint_Vector_Times' + suffix + '.csv','rb'),delimiter=',',skiprows=0)

staticSetData = numpy.loadtxt(open(prefix + 'StaticPoint_Set_Times' + suffix + '.csv','rb'),delimiter=',',skiprows=0)
dynamicSetData = numpy.loadtxt(open(prefix + 'DynamicPoint_Set_Times' + suffix + '.csv','rb'),delimiter=',',skiprows=0)
arrayOfPointersSetData = numpy.loadtxt(open(prefix + 'ArrayOfPointersPoint_Set_Times' + suffix + '.csv','rb'),delimiter=',',skiprows=0)
listSetData = numpy.loadtxt(open(prefix + 'ListPoint_Set_Times' + suffix + '.csv','rb'),delimiter=',',skiprows=0)

improved_ArrayOfPointersSetData = numpy.loadtxt(open(prefix + 'Improved_ArrayOfPointersPoint_Set_Times' + suffix + '.csv','rb'),delimiter=',',skiprows=0)


# all non-static vectors versus static vector
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(log10(numberOfObjectsData), numberOfNeighborsData, (dynamicVectorData / staticVectorData), rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('log10(number of objects)')
plt.ylabel('number of neighbors')
ax.set_zlabel('slowdown')
plt.title('dynamicVector versus staticVector')
filename = outputPrefix + 'dynamicVector_vs_staticVector' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(log10(numberOfObjectsData), numberOfNeighborsData, (arrayOfPointersVectorData / staticVectorData), rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('log10(number of objects)')
plt.ylabel('number of neighbors')
ax.set_zlabel('slowdown')
plt.title('arrayOfPointersVector versus staticVector')
filename = outputPrefix + 'arrayOfPointersVector_vs_staticVector' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(log10(numberOfObjectsData), numberOfNeighborsData, (listVectorData / staticVectorData), rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('log10(number of objects)')
plt.ylabel('number of neighbors')
ax.set_zlabel('slowdown')
plt.title('listVector versus staticVector')
filename = outputPrefix + 'listVector_vs_staticVector' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename







# all non-static sets versus static set
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(log10(numberOfObjectsData), numberOfNeighborsData, (dynamicSetData / staticSetData), rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('log10(number of objects)')
plt.ylabel('number of neighbors')
ax.set_zlabel('slowdown')
plt.title('dynamicSet versus staticSet')
filename = outputPrefix + 'dynamicSet_vs_staticSet' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(log10(numberOfObjectsData), numberOfNeighborsData, (arrayOfPointersSetData / staticSetData), rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('log10(number of objects)')
plt.ylabel('number of neighbors')
ax.set_zlabel('slowdown')
plt.title('arrayOfPointersSet versus staticSet')
filename = outputPrefix + 'arrayOfPointersSet_vs_staticSet' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(log10(numberOfObjectsData), numberOfNeighborsData, (listSetData / staticSetData), rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('log10(number of objects)')
plt.ylabel('number of neighbors')
ax.set_zlabel('slowdown')
plt.title('listSet versus staticSet')
filename = outputPrefix + 'listSet_vs_staticSet' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename





# static set versus static vector, or how bad you screw up by using a set
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(log10(numberOfObjectsData), numberOfNeighborsData, (staticSetData / staticVectorData), rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('log10(number of objects)')
plt.ylabel('number of neighbors')
ax.set_zlabel('slowdown')
plt.title('staticSet versus staticVector')
filename = outputPrefix + 'staticSet_vs_staticVector' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename





# worst one versus best one
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(log10(numberOfObjectsData), numberOfNeighborsData, (listSetData / staticVectorData), rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('log10(number of objects)')
plt.ylabel('number of neighbors')
ax.set_zlabel('slowdown')
plt.title('listSet versus staticVector')
filename = outputPrefix + 'listSet_vs_staticVector' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename







# improved version
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=13, azim=-30)
surf = ax.plot_surface(log10(numberOfObjectsData), numberOfNeighborsData, (improved_ArrayOfPointersSetData / staticVectorData), rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0.5, antialiased=False)
plt.xlabel('log10(number of objects)')
plt.ylabel('number of neighbors')
ax.set_zlabel('slowdown')
plt.title('improved arrayOfPointersSet vs staticVector')
filename = outputPrefix + 'improvedArrayOfPointersSet_vs_staticVector' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename



colors = cm.jet(numpy.linspace(1, 0, 9))
colorIter = iter(colors)

plt.figure(figsize=(12,6))
ax = plt.subplot(111)
plt.xscale('log')
plt.yscale('log')
legendNames = []
plt.plot(numberOfObjectsData[:,-1], listSetData[:,-1] / staticVectorData[:,-1], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('list set')
plt.plot(numberOfObjectsData[:,-1], listVectorData[:,-1] / staticVectorData[:,-1], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('list vector')
plt.plot(numberOfObjectsData[:,-1], arrayOfPointersSetData[:,-1] / staticVectorData[:,-1], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('arrayOfPointers set')
plt.plot(numberOfObjectsData[:,-1], arrayOfPointersVectorData[:,-1] / staticVectorData[:,-1], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('arrayOfPointers vector')
plt.plot(numberOfObjectsData[:,-1], dynamicSetData[:,-1] / staticVectorData[:,-1], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('dynamic set')
plt.plot(numberOfObjectsData[:,-1], dynamicVectorData[:,-1] / staticVectorData[:,-1], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('dynamic vector')
plt.plot(numberOfObjectsData[:,-1], staticSetData[:,-1] / staticVectorData[:,-1], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('static set')
plt.plot(numberOfObjectsData[:,-1], improved_ArrayOfPointersSetData[:,-1] / staticVectorData[:,-1], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('improved arrayOfPointers set')
plt.ylim([1e-1, 1e3])
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.65, box.height])
ax.legend(legendNames, loc='center right', bbox_to_anchor=(1.70, 0.5))
plt.title('slowdown w.r.t. vector of statically-sized points, %d neighbors' % numberOfNeighborsData[0,-1])
plt.xlabel('numberOfObjects', fontsize=16)
plt.ylabel('slowdown', fontsize=16)
filename = outputPrefix + '2d_slowdownSummary_bigNumberOfNeighbors' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename

colorIter = iter(colors)
plt.figure(figsize=(12,6))
ax = plt.subplot(111)
plt.xscale('log')
plt.yscale('log')
legendNames = []
plt.plot(numberOfObjectsData[:,0], listSetData[:,0] / staticVectorData[:,0], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('list set')
plt.plot(numberOfObjectsData[:,0], listVectorData[:,0] / staticVectorData[:,0], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('list vector')
plt.plot(numberOfObjectsData[:,0], arrayOfPointersSetData[:,0] / staticVectorData[:,0], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('arrayOfPointers set')
plt.plot(numberOfObjectsData[:,0], arrayOfPointersVectorData[:,0] / staticVectorData[:,0], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('arrayOfPointers vector')
plt.plot(numberOfObjectsData[:,0], dynamicSetData[:,0] / staticVectorData[:,0], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('dynamic set')
plt.plot(numberOfObjectsData[:,0], dynamicVectorData[:,0] / staticVectorData[:,0], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('dynamic vector')
plt.plot(numberOfObjectsData[:,0], staticSetData[:,0] / staticVectorData[:,0], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('static set')
plt.plot(numberOfObjectsData[:,0], improved_ArrayOfPointersSetData[:,0] / staticVectorData[:,0], color=next(colorIter), hold='on', linewidth=2)
legendNames.append('improved arrayOfPointers set')
plt.ylim([1e-1, 1e3])
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.65, box.height])
ax.legend(legendNames, loc='center right', bbox_to_anchor=(1.70, 0.5))
plt.title('slowdown w.r.t. vector of statically-sized points, %d neighbors' % numberOfNeighborsData[0,0])
plt.xlabel('numberOfObjects', fontsize=16)
plt.ylabel('slowdown', fontsize=16)
filename = outputPrefix + '2d_slowdownSummary_smallNumberOfNeighbors' + suffix + '.pdf'
plt.savefig(filename)
print 'saved file to %s' % filename
