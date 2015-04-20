#!/usr/bin/env python2.7

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
import itertools
import csv
from mpl_toolkits.mplot3d import Axes3D
from numpy import log10

# for floating point comparisons
threshold = 1e-11

# TODO:
#   Get plot_surface to work, it should work and would be better than the triangle approach
#   Verify that setting static points is working properly
#   Make latency into ms, not s
#   Get z setting labeling to work


class ColSettings:
    """ Settings object to contain properties of a data dimension """

    def __init__(self, name, scale="linear", 
                 defaultValue=0):
        self.name = name
        self.scale = scale
        self.defaultValue = defaultValue


# Rows at the beginning of the file while the protocol is still trying to figure out what it should be doing
firstRowsOfJunk = 1500
# Settings of computed data dimensions. A set of graphs will be computed for each computed data dimension.
computedColSettings = [ColSettings("Mean of NTP Uncertainty (ms)"),
                       ColSettings("Max of NTP Uncertainty (ms)"),
                       ColSettings("STD of NTP Uncertainty (ms)"),

                       ColSettings("Mean of abs NTP Measured Time Offset (ms)"),
                       ColSettings("Max of abs NTP Measured Time Offset (ms)"),
                       ColSettings("STD of abs NTP Measured Time Offset (ms)"),

                       ColSettings("Mean of abs Absolute Time Offset (ms)"),
                       ColSettings("Max of abs Absolute Time Offset (ms)"),
                       ColSettings("STD of abs Absolute Time Offset (ms)"),

                       ColSettings("Mean of Safety Buffer (ms)"),
                       ColSettings("Max of Safety Buffer (ms)"),
                       ColSettings("Min of Safety Buffer (ms)"),
                       ColSettings("STD of Safety Buffer (ms)")]
dimensionsOfComputedData = len(computedColSettings)


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

    with open(os.path.join(path, "log.ntp_maxerror")) as fdError:
        with open(os.path.join(path, "log.ntp_offset")) as fdNTPOffset:
            with open(os.path.join(path, "log.timeoffset")) as fdRealOffset:

                it = itertools.count(0)

                errorData = loadFile(fdError) / 1000.0
                dataArray[index][paramsCount+it.next()] = numpy.mean(errorData)
                dataArray[index][paramsCount+it.next()] = numpy.amax(errorData)
                dataArray[index][paramsCount+it.next()] = numpy.std(errorData)
            
                # take absolute values as offsets can be positive or negative
                ntpOffsetData = numpy.fabs(loadFile(fdNTPOffset)) * 1000
                dataArray[index][paramsCount+it.next()] = numpy.mean(ntpOffsetData)
                dataArray[index][paramsCount+it.next()] = numpy.amax(ntpOffsetData)
                dataArray[index][paramsCount+it.next()] = numpy.std(ntpOffsetData)

                # take absolute values as timeoffsets can be positive or negative
                realOffsetData = numpy.fabs(loadFile(fdRealOffset)) * 1000
                dataArray[index][paramsCount+it.next()] = numpy.mean(realOffsetData)
                dataArray[index][paramsCount+it.next()] = numpy.amax(realOffsetData)
                dataArray[index][paramsCount+it.next()] = numpy.std(realOffsetData)

                safetyBufferData = errorData - numpy.fabs(ntpOffsetData - realOffsetData)
                dataArray[index][paramsCount+it.next()] = numpy.mean(safetyBufferData)
                dataArray[index][paramsCount+it.next()] = numpy.amax(safetyBufferData)
                dataArray[index][paramsCount+it.next()] = numpy.amin(safetyBufferData)
                dataArray[index][paramsCount+it.next()] = numpy.std(safetyBufferData)



    if (index % 100 == 0):
        print "Processed folder %s" % index



def make3dPlotTrisurf(dataArray, cols, fixed, colSettings, captionText, pathRoot):
    """ expects a 3-ple of cols """

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.view_init(elev=13, azim=-30)

    filteredArray = dataArray
    for col in fixed:
        filteredArray = filteredArray[ (colSettings[col].defaultValue-threshold < filteredArray[:,col]) & 
                                       (colSettings[col].defaultValue+threshold > filteredArray[:,col]) ]

    x = filteredArray[:,cols[0]]
    y = filteredArray[:,cols[1]]
    z = filteredArray[:,cols[2]]

    xSettings = colSettings[cols[0]]
    ySettings = colSettings[cols[1]]
    zSettings = colSettings[cols[2]]

    xlabel = xSettings.name
    ylabel = ySettings.name
    zlabel = zSettings.name

    # Hack to work around https://github.com/matplotlib/matplotlib/issues/209
    if (xSettings.scale == 'log'):
        x = log10(x)
        xlabel = 'Log10 of ' + xlabel
    if (ySettings.scale == 'log'):
        y = log10(y)
        ylabel = 'Log10 of ' + ylabel
    if (zSettings.scale == 'log'):
        z = log10(z)
        zlabel = 'Log10 of ' + zlabel

    surf = ax.plot_trisurf(x, y, z, cmap=cm.coolwarm, linewidth=0.1)

    # Customize plot
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    ax.set_zlabel(zlabel)

    strippedNames = map(lambda x: x.split('(')[0].strip(), [zSettings.name, ySettings.name, xSettings.name])

    fixedText = "\nFixed Parameters = ("
    for col in fixed:
        fixedText += " " + colSettings[col].name + ": " + str(colSettings[col].defaultValue) + ","
    fixedText = fixedText[:-1] + " )"

    title = "{} vs {} vs {}".format(*strippedNames)
    if (len(title) > 60): 
        title = "{} vs {}\nvs {}".format(*strippedNames)
    plt.title(title)

    #   commented out for plots for poster
#    plt.figtext(.1, .8, captionText + fixedText, verticalalignment=u'baseline', size=u'xx-small')
    filename = "{}_{}_{}_trisurf.png".format(*strippedNames)
    plt.savefig(os.path.join(pathRoot, filename))
    plt.close()
    print 'saved file to %s' % filename

def make3dPlotScatter(dataArray, cols, fixed, colSettings, captionText, pathRoot):
    """ expects a 3-ple of cols """

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.view_init(elev=13, azim=-30)

    filteredArray = dataArray
    for col in fixed:
        filteredArray = filteredArray[ (colSettings[col].defaultValue-threshold < filteredArray[:,col]) & 
                                       (colSettings[col].defaultValue+threshold > filteredArray[:,col]) ]

    x = filteredArray[:,cols[0]]
    y = filteredArray[:,cols[1]]
    z = filteredArray[:,cols[2]]

    xSettings = colSettings[cols[0]]
    ySettings = colSettings[cols[1]]
    zSettings = colSettings[cols[2]]

    xlabel = xSettings.name
    ylabel = ySettings.name
    zlabel = zSettings.name

    # Hack to work around https://github.com/matplotlib/matplotlib/issues/209
    if (xSettings.scale == 'log'):
        x = log10(x)
        xlabel = 'Log10 of ' + xlabel
    if (ySettings.scale == 'log'):
        y = log10(y)
        ylabel = 'Log10 of ' + ylabel
    if (zSettings.scale == 'log'):
        z = log10(z)
        zlabel = 'Log10 of ' + zlabel

    surf = ax.scatter(x, y, z, cmap=cm.jet, linewidth=0.2)

    # import pdb; pdb.set_trace()

    # Customize plot
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    ax.set_zlabel(zlabel)

    strippedNames = map(lambda x: x.split('(')[0].strip(), [zSettings.name, ySettings.name, xSettings.name])

    fixedText = "\nFixed Parameters = ("
    for col in fixed:
        fixedText += " " + colSettings[col].name + ": " + str(colSettings[col].defaultValue) + ","
    fixedText = fixedText[:-1] + " )"

    # Graphs are about 60 title-characters wide, and don't word wrap automatically
    title = "{} vs {} vs {}".format(*strippedNames)
    if (len(title) > 60): 
        title = "{} vs {}\nvs {}".format(*strippedNames)
    plt.title(title)

    # plt.figtext(.1, .8, captionText + fixedText, verticalalignment=u'baseline', size=u'xx-small')
    filename = "{}_{}_{}_scatter.png".format(*strippedNames)
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

def main(rootpath, captionPath, outPath, defaults):
    # split up defaults
    paramNamesList = defaults[0::3]
    paramScaleList = defaults[1::3]
    defaultVals = map(float, defaults[2::3])
    paramSettings = []
    for i in range(len(paramNamesList)):
        paramSettings.append(ColSettings(paramNamesList[i], scale=paramScaleList[i], defaultValue=defaultVals[i]))

    # TODO: refactor
    # special setting for clock wander, axis units overlap axis label
    paramSettings[0].name = "\n\n" + paramSettings[0].name

    # calculate where to put the graphs
    outputDir = os.path.join(outPath, getFolderName(os.path.realpath(rootpath)))
    if (not os.path.isdir(outputDir)): 
        os.mkdir(outputDir)

    # grab the caption text
    with open(captionPath) as f:
        captionText = f.read()

    rootdir = os.listdir(rootpath)
    dirs = filter(lambda fldr: os.path.isdir(os.path.join(rootpath, fldr)), rootdir)

    dataArray = numpy.empty((len(dirs), len(paramNamesList) + dimensionsOfComputedData))

    # fill out the array with the data in folders
    # map(lambda index: processFolder(rootpath, dirs[index], dataArray, index), range(len(dirs)))
    map(lambda index: processFolder(rootpath, dirs[index], dataArray, index), range(400))

    # Do special processing on this data


    # make the graphs
    numberOfInputParams = len(paramNamesList)
    
    # compute settings objects for each possible axis
    allSettings = paramSettings + computedColSettings

    # pairs of input parameters
    combinationsOfInputParams = [item for item in itertools.combinations(xrange(numberOfInputParams), 2)]

    # Iterate over all combinations of inputs and outputs, choosing one output and 2 inputs
    for outputCol in range(numberOfInputParams, dimensionsOfComputedData + numberOfInputParams):
        for inputComb in combinationsOfInputParams:

            # Find the set of parameters that need to be fixed for this graph
            fixed = list(set(range(numberOfInputParams)) - set(inputComb))
            fixed.sort()

            # Make our plots
            make3dPlotScatter(dataArray, inputComb+(outputCol,), fixed, allSettings, captionText, outputDir)
            make3dPlotTrisurf(dataArray, inputComb+(outputCol,), fixed, allSettings, captionText, outputDir)



if __name__=="__main__":
    if (len(sys.argv) < 4):
        print "Please run with"
        print "\t 1. a directory argument containing the relevant directory structure"
        print "\t 2. a file that contains a text caption to be appended to graphs"
        print "\t 3. a directory path where figures should be saved"
        print "\t 4. axis labels for simulation parameters followed by default for holding constant"
        print
        print 'Example: 3dPlot.py ./data ./caption_text ./figures "param1 (feet)" "log" 3.4 "param2 (s)" "linear" 1.2e7 ... "paramN (k)" "log" 0'
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
