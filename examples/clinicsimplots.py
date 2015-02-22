import sys
import numpy as np
import matplotlib.pyplot as plt

def main():
    fileName = "tmp/log.timeoffset"
    fileName2 = "tmp/log.ntp_maxerror"
    fileName3 = "tmp/log.ntp_offset"

    f = open(fileName, 'r')
    f3 = open(fileName3, 'r')
    contents = f.read()
    contents3 = f3.read()
    f.close()
    f3.close()
    lines = str.split(contents, "\n")
    lines3 = str.split(contents3, "\n")
    values = [float(x.split()[1]) for x in lines[:-1]]
    values3 = [float(x.split()[1]) for x in lines3[:-1]]
    finalValues = []
    for i in range(len(values)):
        finalValues += [values[i] - values3[i]]
        print values[i] - values3[i]
    # finalValues = [x - y for x in valuesd for y in values3]
    t = np.arange(0., 20001., 1)
    print "Time", len(t)
    print "Values", len(finalValues)
    plt.plot(t, finalValues, 'g')

    f2 = open(fileName2, 'r')

    contents = f2.read()
    f2.close()
    lines = str.split(contents, "\n")
    values = [float(x.split()[1])/1000000.0 for x in lines[:-1]]
    t = np.arange(0., 20001., 1)

    plt.plot(t, values, 'b')
    negValues = [(-1.0 * x) for x in values]
    plt.plot(t, negValues, 'r')

    # allLines = str.split(contents, "\n")
    # allLines = [x.split() for x in allLines]
    # sendLines = [x for x in allLines[:-1] if (int(x[1]) == 2)]
    # recLines = [x for x in allLines[:-1] if (int(x[2]) == 2)]

    # uncertValues = []
    # for i in range(len(recLines) - 1):
    #     sendTime = float(sendLines[i][0])
    #     nextSendTime = float(sendLines[i+1][0])
    #     recTime = float(recLines[i][0])
    #     if (recTime - sendTime) == 0:
    #     # if (recTime - sendTime + float(values[len(uncertValues)])) < 0:
    #         print sendTime
    #         print recTime
    #         print float(values[len(uncertValues)])
    #         print sendLines[i]
    #         print recLines[i]
    #         print
    #         print
    #     uncertValues += [recTime - sendTime]*(int(nextSendTime - sendTime))

    # plt.plot(t[:len(uncertValues)], uncertValues)
    # negUncertValues = [-1*x for x in uncertValues]
    # plt.plot(t[:len(negUncertValues)], negUncertValues)
    # plt.plot(t, [0]*len(t))



    plt.axis([0, 20000, -0.1, 0.1])
    plt.plot(t, [0]*len(t), '-')

    plt.xlabel("Time (s)")
    plt.ylabel("Offset, Uncertainty (s)")
    plt.title("(NTP Offset - True Offset) vs Time")

    plt.show()

def main2():
    fileName = "tmp/log.ntp_maxerror"
    fileName2 = "tmp/log.packetdelays"

    f = open(fileName, 'r')
    contents = f.read()
    f.close()
    lines = str.split(contents, "\n")
    values = [float(x.split()[1])/1000000.0 for x in lines[:-1]]
    t = np.arange(0., 20001., 1)

    plt.plot(t, values)

    f2 = open(fileName2, 'r')

    contents = f2.read()
    f2.close()

    allLines = str.split(contents, "\n")
    allLines = [x.split() for x in allLines]
    sendLines = [x for x in allLines[:-1] if (int(x[1]) == 2)]
    recLines = [x for x in allLines[:-1] if (int(x[2]) == 2)]

    uncertValues = []
    for i in range(len(recLines) - 1):
        sendTime = float(sendLines[i][0])
        nextSendTime = float(sendLines[i+1][0])
        recTime = float(recLines[i][0])
        uncertValues += [recTime - sendTime]*(int(nextSendTime - sendTime))

    plt.plot(t[:len(uncertValues)], uncertValues, '.')
    plt.axis([0, 20000, 0,0.1])
    plt.xlabel("Time (s)")
    plt.ylabel("Uncertainty (s)")
    plt.title("Uncertainty and Latency vs. Time")

    plt.show()


if __name__ == "__main__":
    main2()
