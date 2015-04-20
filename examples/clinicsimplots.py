#!/usr/bin/env python2

import sys
import numpy as np
import matplotlib.pyplot as plt
import pylab

realOffsetFileName = "tmp/log.timeoffset"
ntpOffsetFileName = "tmp/log.ntp_offset"
maxErrorFileName = "tmp/log.ntp_maxerror"
packetDelayFileName = "tmp/log.packetdelays"

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

def plotNTPVsRealOffset():
    with open(realOffsetFileName, 'r') as offsetFile:
        with open(ntpOffsetFileName, 'r') as ntpFile:

            realOffsetFileContents = offsetFile.read()
            ntpFileContents = ntpFile.read()

            realOffsetLines = str.split(realOffsetFileContents, "\n")
            ntpOffsetLines = str.split(ntpFileContents, "\n")

            # We pull out the NTP offset and real offset values from the 2nd node 
            ntpOffsetValues = [float(x.split()[1]) for x in realOffsetLines[:-1]]
            realOffsetValues = [float(x.split()[1]) for x in ntpOffsetLines[:-1]]

            # stores the difference between the NTP offset and the real offset
            offsetDiffValues = []

            for i in range(len(ntpOffsetValues)):
                offsetDiffValues += [ntpOffsetValues[i] - realOffsetValues[i]]

            # We make 1 second time values from 0 to 20001
            timeValues = np.arange(0., 20001., 1)

            plt.plot(timeValues, offsetDiffValues, 'g')

            errorFile = open(maxErrorFileName, 'r')
            errorContents = errorFile.read()
            errorFile.close()

            errorLines = str.split(errorContents, "\n")
            errorValues = [float(x.split()[1])/1000000.0 for x in errorLines[:-1]]

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

def plotLatencyVsError():
    ntpFile = open(ntpOffsetFileName, 'r')
    ntpContents = ntpFile.read()
    ntpFile.close()

    ntpLines = str.split(ntpContents, "\n")
    # we need to convert the values to seconds rather than microseconds
    ntpValues = [float(x.split()[1]) for x in ntpLines[:-1]]

    # We make 1 second time values from 0 to 20001
    timeValues = np.arange(0., 20001., 1)

    plt.plot(timeValues, ntpValues, 'r')

    packetFile = open(packetDelayFileName, 'r')
    packetContents = packetFile.read()
    packetFile.close()

    allPacketLines = [x.split() for x in packetContents.split("\n")]
    # We look to see if the second node is in the send or receive column
    # If so, we put that line in the corresponding list of lines from the file.
    sendLines = [x for x in allPacketLines[:-1] if (int(x[1]) == 2)]
    recLines = [x for x in allPacketLines[:-1] if (int(x[2]) == 2)]

    roundTripValues = []
    for i in range(len(recLines) - 1):
        sendTime = float(sendLines[i][0])
        nextSendTime = float(sendLines[i+1][0])

        sendDelay = float(sendLines[i][3])
        recDelay = float(recLines[i][3])
        # We want to create (nextSendTime - sendTime) values of the round
        # trip time so that our plot will draw a line at those times.
        roundTripValues += [sendDelay + recDelay]*(int(nextSendTime - sendTime))

    plt.plot(timeValues[:len(roundTripValues)], roundTripValues, 'g.')

    plt.axis([0, 20000, 0,0.01])
    plt.xlabel("Time (s)")
    plt.ylabel("Uncertainty (s)")
    plt.title("Uncertainty and Latency vs. Time")
    pylab.savefig("images/latency.png")

def extractOverviewOffsetData():
    offsetFile = open(realOffsetFileName, 'r')
    ntpFile = open(ntpOffsetFileName, 'r')
    errorFile = open(maxErrorFileName, 'r')

    realOffsetFileContents = offsetFile.read()
    ntpFileContents = ntpFile.read()
    errorContents = errorFile.read()

    offsetFile.close()
    ntpFile.close()
    errorFile.close()

    realOffsetLines = str.split(realOffsetFileContents, "\n")
    ntpOffsetLines = str.split(ntpFileContents, "\n")
    errorLines = str.split(errorContents, "\n")

    # We pull out the NTP offset and real offset values from the 2nd node 
    # We skip the last line in these values because it is an empty value
    ntpOffsetValues = []
    realOffsetValues = []
    errorValues = []
    offsetBufferValues = []
    for i in range(1,9):
        ntpOffsetValues += [float(x.split()[i]) for x in ntpOffsetLines[1500:-1]]
        realOffsetValues += [float(x.split()[i]) for x in realOffsetLines[1500:-1]]
        errorValues += [float(x.split()[i])/1000000.0 for x in errorLines[1500:-1]]
    for i in range(len(ntpOffsetValues)):
        if (errorValues[i] - abs(ntpOffsetValues[i] - realOffsetValues[i])) <= 0:
            print "BELOW 0!!!!"
            print i
            print errorValues[i] - abs(ntpOffsetValues[i] - realOffsetValues[i])
        offsetBufferValues += [errorValues[i] - abs(ntpOffsetValues[i] - realOffsetValues[i])]

  #  plt.plot(ntpOffsetValues, 'r')
  #  plt.plot(realOffsetValues, 'g')
  #  plt.plot(errorValues, 'b')
 #   plt.plot(offsetBufferValues, 'y')

    average = sum(errorValues) / float(len(errorValues))
    stdDev = np.std(errorValues)

    print "Max:", max(errorValues)
    print "+Standard Deviation:", average + stdDev
    print "Average:", average
    print "-Standard Deviation:", average - stdDev
    print "Min:", min(errorValues)

#    plt.show()


def main():
    # plotNTPVsRealOffset()
    # plotLatencyVsError()
    extractOverviewOffsetData()


if __name__ == "__main__":
    main()
