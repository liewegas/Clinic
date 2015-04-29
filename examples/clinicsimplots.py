#!/usr/bin/env python2

# clinicsimplots.py contains a number of functions that analyze output from the clknetsim
# simulations and produces plots and statistics about that data. It requires
# data from:
#     1) log.timeoffset
#     2) log.ntp_offset
#     3) log.ntp_maxerror
#     4) log.packetdelays
# which are all created by clknetsim. The filepaths need to be specified in the
# arguments to the program. The plots are saved in the directory
# that contains clinicsimplots.py. The plots and stats that are generated are 
# specified in the function comments.

import sys
import numpy as np
import matplotlib.pyplot as plt
import pylab
import argparse


# global filepath variables
realOffsetFilePath = ""
ntpOffsetFilePath = ""
maxErrorFilePath = ""
packetDelayFilePath = ""

def getValuesFromFile(fileName, valueIndex):
    with open(fileName, 'r') as theFile:
        contents = theFile.read()
        lines = contents.split("\n")
        # This line:
        #   1) splits each line into the space separated values in the file
        #   2) extracts the value at the given value index
        #   3) converts that value to a float
        # it also ignores the last line of the file, because the last line is blank
        values = [float(line.split()[valueIndex]) for line in lines[:-1]]
        return values


# We use this function to plot graphs that show how NTP's actual error in time
# synchronization compares to the uncertainty range that it provides. The 
# actual error is the difference between the "real" network time and what NTP
# thinks the time is. Since that difference can be positive or negative, we
# plot the uncertainty and the uncertainty negated, so that we can see if the
# error stays within the uncertainty range.
def plotNTPVsRealOffset():
    ntpOffsetValues = getValuesFromFile(ntpOffsetFilePath, 1)
    realOffsetValues = getValuesFromFile(realOffsetFilePath, 1)
    errorValues = getValuesFromFile(maxErrorFilePath, 1)
    # These values are in microseconds; we want them in seconds.
    errorValues = [x/1000000.0 for x in errorValues]

    # stores the difference between the NTP offset and the real offset
    offsetDiffValues = []

    for i in range(len(ntpOffsetValues)):
        offsetDiffValues += [ntpOffsetValues[i] - realOffsetValues[i]]

    # We make 1 second time values from 0 to 20001
    timeValues = np.arange(0., 20001., 1)

    plt.plot(timeValues, offsetDiffValues, 'g')
    plt.plot(timeValues, errorValues, 'b')
    # We also want to plot the negative values
    negErrorValues = [(-1.0 * x) for x in errorValues]
    plt.plot(timeValues, negErrorValues, 'r')


    plt.axis([0, 20000, -0.01, 0.01])
    # plot a line at 0
    plt.plot(timeValues, [0]*len(timeValues), '-')

    plt.xlabel("Time (s)")
    plt.ylabel("Offset, Uncertainty (s)")
    plt.title("(NTP Offset - True Offset) vs Time")
    pylab.savefig("images/offsetvstime.png")
    plt.clf()


# This function plots uncertainty values and network latency values together
# over time to compare how those values are related.
def plotLatencyVsError():

    ntpValues = getValuesFromFile(ntpOffsetFilePath, 1)

    # We make 1 second time values from 0 to 20001
    timeValues = np.arange(0., 20001., 1)

    plt.plot(timeValues, ntpValues, 'r')

    # The lines that contain the packet being sent/received information
    # We instantiate these in the next block.
    sendLines = []
    recLines = []

    with open(packetDelayFilePath, 'r') as packetFile:
        packetContents = packetFile.read()

        allPacketLines = [x.split() for x in packetContents.split("\n")]
        # We look to see if the second node is in the send or receive column
        # If so, we put that line in the corresponding list of lines from the file.
        sendLines = [x for x in allPacketLines[:-1] if (int(x[1]) == 2)]
        recLines = [x for x in allPacketLines[:-1] if (int(x[2]) == 2)]

    # We want to look at the round trip time the packet took to go from the
    # node to the server and back. We exclude time that the packet spent in
    # the server.
    roundTripValues = []
    for i in range(len(recLines) - 1):
        sendTime = float(sendLines[i][0])
        nextSendTime = float(sendLines[i+1][0])

        sendDelay = float(sendLines[i][3])
        recDelay = float(recLines[i][3])
        # To ensure the plot looks good, we need to add N values of the 
        # round trip time to roundTripValues, where:
        #       N = (nextSendTime - sendTime) 

        roundTripValues += [sendDelay + recDelay]*(int(nextSendTime - sendTime))

    plt.plot(timeValues[:len(roundTripValues)], roundTripValues, 'g.')

    plt.axis([0, 20000, 0,0.01])
    plt.xlabel("Time (s)")
    plt.ylabel("Uncertainty (s)")
    plt.title("Uncertainty and Latency vs. Time")
    pylab.savefig("images/latency.png")


# This function plots four values:
# 1) NTP's estimate for the clock's offset from "real" network time
# 2) The clock's actual offset from "real" network time
# 3) NTP's uncertainty in what the real time is
# 4) The Safety Buffer: the difference between NTP's uncertainty and the
#    difference between NTP's estimate for the offset and the actual offset.
#    More mathematically, using the numbering here to represent the values:
#             Safety Buffer = [3] - |[2] - [1]|
# So long as the safety buffer is positive, then NTP is functioning as it is
# supposed to. If there is ever a moment when NTP fails to maintain the error
# within its uncertainty (i.e. the safety buffer is negative), a warning is 
# printed, with the value index and the value.
#
# If there is more than one node in the system, then the values are plotted
# sequentially, i.e. the first node's values are plotted first, then the second
# node, then the third, etc.
#
# After the plot is made, five values are printed: the safety buffers maximum
# value, its minimum value, its average, and its average +/- its standard
# deviation. 
def plotAndExtractSafetyBufferData():
    ntpOffsetValues = []
    realOffsetValues = []
    errorValues = []
    safetyBufferValues = []

    numNodes = 0

    # all of this is done to calculate the number of nodes...
    with open(ntpOffsetFilePath, 'r') as theFile:
        firstLine = theFile.readline()
        numNodes = len(firstLine.split())

    # We ignore the first 1500 values because NTP needs to take that time to
    # synchronize the nodes. Those values aren't valid.
    for i in range(1, numNodes):
        ntpOffsetValues += getValuesFromFile(ntpOffsetFilePath, i)[1500:]
        realOffsetValues += getValuesFromFile(realOffsetFilePath, i)[1500:]
        errorValues += getValuesFromFile(maxErrorFilePath, i)[1500:]

    # We convert the errorValues from microseconds to seconds.
    errorValues = [x/1000000.0 for x in errorValues]

    for i in range(len(ntpOffsetValues)):
        safetyBufferValue = errorValues[i] - abs(ntpOffsetValues[i] - realOffsetValues[i])
        if safetyBufferValue < 0:
            print "Warning: Negative Safety Buffer Found"
            print "\tValue Index: ", i
            print "\tValue:", safetyBufferValue
        safetyBufferValues += [safetyBufferValue]

    plt.plot(ntpOffsetValues, 'r')
    plt.plot(realOffsetValues, 'g')
    plt.plot(errorValues, 'b')
    plt.plot(safetyBufferValues, 'y')

    average = sum(safetyBufferValues) / float(len(safetyBufferValues))
    stdDev = np.std(safetyBufferValues)

    print "Safety Buffer Stats:"
    print "Max:", max(safetyBufferValues)
    print "+Standard Deviation:", average + stdDev
    print "Average:", average
    print "-Standard Deviation:", average - stdDev
    print "Min:", min(safetyBufferValues)

    pylab.savefig("images/safetybuffer.png")

def main():
    global realOffsetFilePath, ntpOffsetFilePath, maxErrorFilePath, packetDelayFilePath
    parser = argparse.ArgumentParser()

    # creates an argument that captures the directory the logged data files are in
    parser.add_argument("-d", "--directory", 
        action = 'store',
        default = "tmp",
        help = "specifies the directory for the logged data files.\
                The directory must include the following files: \
                \n\tlog.timeoffset\
                \n\tlog.ntp_offset\
                \n\tlog.ntp_maxerror\
                \n\tlog.packetdelays")

    # If set, it runs plotNTPVsRealOffset
    parser.add_argument("-p", "--plotOffsets", action = "store_true",
                        help = "use to plot NTP offset and the real offseti over time")
    # If set, it runs plotLatencyVsError
    parser.add_argument("-l", "--latency", action = "store_true",
                        help = "use to plot the latency and the uncertainty over time")
    # If set, it runs plotAndExtractSafetyBufferData
    parser.add_argument("-o", "--overview", action = "store_true",
                        help = "use to plot the safety buffer over time and to extract data about the safety buffer")

    argSpace = parser.parse_args()

    # stores the file paths in the proper variables
    realOffsetFilePath = argSpace.directory + "/log.timeoffset"
    ntpOffsetFilePath = argSpace.directory + "/log.ntp_offset"
    maxErrorFilePath = argSpace.directory + "/log.ntp_maxerror"
    packetDelayFilePath = argSpace.directory + "/log.packetdelays"


    if argSpace.plotOffsets:
        print "Plotting NTP offset and the real offset over time"
        plotNTPVsRealOffset()
    if argSpace.latency:
        print "Plotting the latency and the uncertainty over time"
        plotLatencyVsError()
    if argSpace.overview:
        print "Plotting the safety buffer and extracting data about the safety buffer"
        plotAndExtractSafetyBufferData()


if __name__ == "__main__":
    main()
