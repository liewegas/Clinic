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

# Boolean to turn on and off captioning of figures
CAPTION = False

# for floating point comparisons
threshold = 1e-11


class ColSettings:
    """ Settings object to contain properties of a data dimension.
        Simply wraps several parameters that each data dimension must
        specify. """

    def __init__(self, name, scale="linear", 
                 defaultValue=0):
        self.name = name
        self.scale = scale
        self.defaultValue = defaultValue


# Rows at the beginning of the file to drop.
# These should be the lines we want to throw out 
# while the protocol is still trying to figure out what it should be doing
firstRowsOfJunk = 1500

# Settings of computed data dimensions. A set of graphs will be computed 
# for each computed data dimension.
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
    """ Returns cols columns of the file at file descriptor fd. 
        By default, just pulls the second column of the file. """

    fileData = numpy.loadtxt(
        fd,
        delimiter='\t',
        skiprows=firstRowsOfJunk,
        usecols = cols)

    return fileData


def processFolder(rootpath, folder, dataArray, index):
    """ Process some hard-coded files in a given folder according to 
        some hard-coded transformations. Specify what values you are interested
        in in this function. 

        rootpath: str -- path to folder (not including folder), 
        folder: str -- name of folder, 
        dataArray: numpy array of the necessary order to hold data,
        index: which dimension to save this set of values into """

    path = os.path.join(rootpath, folder)
    
    # Folders are named with the input parameters of the run they contain.
    # Split the parameters and place them at the relevant index in the matrix.
    params = folder.split('_')
    paramsCount = len(params)
    for i in xrange(paramsCount):
        dataArray[index][i] = float(params[i])

    # Open the files that are relevant to our calculations
    with open(os.path.join(path, "log.ntp_maxerror")) as fdError:
        with open(os.path.join(path, "log.ntp_offset")) as fdNTPOffset:
            with open(os.path.join(path, "log.timeoffset")) as fdRealOffset:

                # Each calculated value needs to go in its own column. 
                # Let's use an iterator to count up. We start at the column
                # after the last input parameter column.
                it = itertools.count(paramsCount)

                # For the parameters read in in this iteration of the simulation,
                # calculate characteristic values. Save them to the appropriate
                # place in the data array we are building.

                # Error Data was reported in microseconds. Switch to milliseconds.
                errorData = loadFile(fdError) / 1000.0
                dataArray[index][it.next()] = numpy.mean(errorData)
                dataArray[index][it.next()] = numpy.amax(errorData)
                dataArray[index][it.next()] = numpy.std(errorData)
            
                # take absolute values as offsets can be positive or negative
                ntpOffsetData = numpy.fabs(loadFile(fdNTPOffset)) * 1000
                dataArray[index][it.next()] = numpy.mean(ntpOffsetData)
                dataArray[index][it.next()] = numpy.amax(ntpOffsetData)
                dataArray[index][it.next()] = numpy.std(ntpOffsetData)

                # take absolute values as timeoffsets can be positive or negative
                realOffsetData = numpy.fabs(loadFile(fdRealOffset)) * 1000
                dataArray[index][it.next()] = numpy.mean(realOffsetData)
                dataArray[index][it.next()] = numpy.amax(realOffsetData)
                dataArray[index][it.next()] = numpy.std(realOffsetData)

                # The safety buffer is calculated from offset data and error data
                safetyBufferData = errorData - numpy.fabs(ntpOffsetData - realOffsetData)
                dataArray[index][it.next()] = numpy.mean(safetyBufferData)
                dataArray[index][it.next()] = numpy.amax(safetyBufferData)
                dataArray[index][it.next()] = numpy.amin(safetyBufferData)
                dataArray[index][it.next()] = numpy.std(safetyBufferData)


    # Every once in awhile, report out an update on our progress.
    if (index % 100 == 0):
        print "Processed folder %s" % index



def make3dPlotTrisurf(dataArray, cols, fixed, colSettings, captionText, pathRoot):
    """ Create and save a 3d graph using triangle interpolation to generate 
        a surface. Uses cols parameter to select columns in dataArray to be 
        graphed. 

        dataArray:  The big array containing all of the data we have read in.
        cols:       Which columns to use in constructing the current graph.
                    Expected to be a 3-ple.
        fixed:      An array of column indices that are to be held at fixed values for
                    constructing this graph. The values to fix these columns at
                    are looked up in colSettings.
        colSettings:    An array that contains settings for each data dimension.
        captionText:    Text to add to the graph, under the tile, probably useful
                        for describing the parameters from which the graph was
                        created.
        pathRoot:   The folder in which to save the graph once it is constructed.
        """

    # Create a figure
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Set the eye perspective
    ax.view_init(elev=13, azim=-30)

    # Filter values we don't care about out of the data array
    filteredArray = dataArray
    for col in fixed:
        filteredArray = filteredArray[ (colSettings[col].defaultValue-threshold < filteredArray[:,col]) & 
                                       (colSettings[col].defaultValue+threshold > filteredArray[:,col]) ]

    # Grab the columns we care about
    x = filteredArray[:,cols[0]]
    y = filteredArray[:,cols[1]]
    z = filteredArray[:,cols[2]]

    # Grab the settings objects we care about
    xSettings = colSettings[cols[0]]
    ySettings = colSettings[cols[1]]
    zSettings = colSettings[cols[2]]

    # Grab the names of the dimensions we care about
    xlabel = xSettings.name
    ylabel = ySettings.name
    zlabel = zSettings.name

    # If we are working with an 'exotic' axis scale, set it up here.
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

    # Actually plot the surface
    surf = ax.plot_trisurf(x, y, z, cmap=cm.coolwarm, linewidth=0.1)

    # Customize plot
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    ax.set_zlabel(zlabel)

    # Take the units and gunk off of the name strings -- some things don't need that stuff
    strippedNames = map(lambda x: x.split('(')[0].strip(), [zSettings.name, ySettings.name, xSettings.name])

    # Make a note on the graph of the parameters that were fixed, and what the values were
    fixedText = "\nFixed Parameters = ("
    for col in fixed:
        fixedText += " " + colSettings[col].name + ": " + str(colSettings[col].defaultValue) + ","
    fixedText = fixedText[:-1] + " )"

    # Build a reasonable title for this graph
    # Graphs are about 60 title-characters wide, and don't word wrap automatically
    title = "{} vs {} vs {}".format(*strippedNames)
    if (len(title) > 60): 
        title = "{} vs {}\nvs {}".format(*strippedNames)
    plt.title(title)

    # Actually insert the caption into the figure
    if (CAPTION):
        plt.figtext(.1, .8, captionText + fixedText, verticalalignment=u'baseline', size=u'xx-small')

    # Name, save, and close the file
    filename = "{}_{}_{}_trisurf.png".format(*strippedNames)
    plt.savefig(os.path.join(pathRoot, filename))
    plt.close()

    # Print out a status message
    print 'saved file to %s' % filename

def make3dPlotScatter(dataArray, cols, fixed, colSettings, captionText, pathRoot):
    """ Create and save a 3d scatter plot of input values.
        Uses cols parameter to select columns in dataArray to be 
        graphed. 

        dataArray:  The big array containing all of the data we have read in.
        cols:       Which columns to use in constructing the current graph.
                    Expected to be a 3-ple.
        fixed:      An array of column indices that are to be held at fixed values for
                    constructing this graph. The values to fix these columns at
                    are looked up in colSettings.
        colSettings:    An array that contains settings for each data dimension.
        captionText:    Text to add to the graph, under the tile, probably useful
                        for describing the parameters from which the graph was
                        created.
        pathRoot:   The folder in which to save the graph once it is constructed.
        """

    # Create a figure
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Set the eye perspective
    ax.view_init(elev=13, azim=-30)

    # Filter values we don't care about out of the data array
    filteredArray = dataArray
    for col in fixed:
        filteredArray = filteredArray[ (colSettings[col].defaultValue-threshold < filteredArray[:,col]) & 
                                       (colSettings[col].defaultValue+threshold > filteredArray[:,col]) ]

    # Grab the columns we care about
    x = filteredArray[:,cols[0]]
    y = filteredArray[:,cols[1]]
    z = filteredArray[:,cols[2]]

    # Grab the settings objects we care about
    xSettings = colSettings[cols[0]]
    ySettings = colSettings[cols[1]]
    zSettings = colSettings[cols[2]]

    # Grab the names of the dimensions we care about
    xlabel = xSettings.name
    ylabel = ySettings.name
    zlabel = zSettings.name

    # If we are working with an 'exotic' axis scale, set it up here.
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

    # Actually plot the surface
    surf = ax.scatter(x, y, z, cmap=cm.jet, linewidth=0.2)

    # import pdb; pdb.set_trace()

    # Customize plot
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    ax.set_zlabel(zlabel)

    # Take the units and gunk off of the name strings -- some things don't need that stuff
    strippedNames = map(lambda x: x.split('(')[0].strip(), [zSettings.name, ySettings.name, xSettings.name])

    # Make a note on the graph of the parameters that were fixed, and what the values were
    fixedText = "\nFixed Parameters = ("
    for col in fixed:
        fixedText += " " + colSettings[col].name + ": " + str(colSettings[col].defaultValue) + ","
    fixedText = fixedText[:-1] + " )"

    # Build a reasonable title for this graph
    # Graphs are about 60 title-characters wide, and don't word wrap automatically
    title = "{} vs {} vs {}".format(*strippedNames)
    if (len(title) > 60): 
        title = "{} vs {}\nvs {}".format(*strippedNames)
    plt.title(title)

    # Actually insert the caption into the figure
    if (CAPTION):
        plt.figtext(.1, .8, captionText + fixedText, verticalalignment=u'baseline', size=u'xx-small')
    
    # Name, save, and close the file
    filename = "{}_{}_{}_scatter.png".format(*strippedNames)
    plt.savefig(os.path.join(pathRoot, filename))
    plt.close()

    # Print out a status message
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
    map(lambda index: processFolder(rootpath, dirs[index], dataArray, index), range(len(dirs)))

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
