#!/usr/bin/env python3

import os
import ipaddress
import subprocess
import datetime
import math

def config1(nodecount, offset, freqexpr, delayexprup, delayexprdown = "", refclockexpr = 0):
    """ Generate client configs """
    conf = ""

    for i in range(1, nodecount + 1):
        conf += "node{}_offset = {}\n".format(i, i - 1)

        if (i == 1): 
            #conf += "node{}_freq = {}\n".format(i, freqexpr)
            conf += "node1_refclock = (* 0 0)\n"
            conf += "node1_refclock = (sum (* 1e-8 (normal)))\n"
            
        else: 
            conf += "node{}_freq = {}\n".format(i, freqexpr)

        conf += "node{}_delay1 = {}\n".format(i, delayexprup)

        if (delayexprdown != ""):
            conf += "node1_delay{} = {}\n".format(i, delayexprdown)
        else:
            conf += "node1_delay{} = {}\n".format(i, delayexprup)

        # if (refclockexpr != ""):
        #     conf += "node{}_refclock = {}\n".format(i, refclockexpr)

    confFile = open("./tmp/conf", 'w')

    confFile.write(conf)

    confFile.close()


    scriptname = "cephntp.dynamic.test"
    createScript(nodecount, scriptname)

    subprocess.check_call("./{}".format(scriptname), 
        shell=True)

# config2 is used to give each node a different file for the delay expression.
# it assumes that the files are of a consistent format.
def config2(nodecount, offset, freqexpr, refclockexpr = 0):
    """ Generate client configs """
    conf = ""

    for i in range(1, nodecount + 1):
        conf += "node{}_offset = {}\n".format(i, i - 1)

        if (i == 1): 
            #conf += "node{}_freq = {}\n".format(i, freqexpr)
            conf += "node1_refclock = (* 0 0)\n"
            conf += "node1_refclock = (sum (* 1e-8 (normal)))\n"
            
        else: 
            conf += "node{}_freq = {}\n".format(i, freqexpr)

        conf += "node{}_delay1 = (file \"../latencydata/latencyValues{}.txt\")\n".format(i, i)
        # we use a different latency file for the return trip than for the initial trip
        conf += "node1_delay{} = (file \"../latencydata/latencyValues{}.txt\")\n".format(i, i + (nodecount - 1))

        # if (refclockexpr != ""):
        #     conf += "node{}_refclock = {}\n".format(i, refclockexpr)

    confFile = open("./tmp/conf", 'w')

    confFile.write(conf)

    confFile.close()


    scriptname = "cephntp.dynamic.test"
    createScript(nodecount, scriptname)

    subprocess.check_call("./{}".format(scriptname), 
        shell=True)

# config3 is used to vary many different parameters for the purpose of running
# multiple simulations in a row.
def config3():
    """ Generate client configs """
    # the number of nodes in our simulation
    nodecount = 2
    time = str(datetime.datetime.now()).replace(" ", "_")

    if (not os.path.isdir("./tmp")):
        os.mkdir("./tmp")
    os.mkdir("./tmp/{}".format(time))

    latencyMeanTimes = [10**((float(x)/10.0) - 5) for x in range(31)]

    # Clock Drift Std Deviation Loop
    for driftStdDev in [1e-8*float(x) for x in range(1,11)]:
        # Latency Alpha Value Loop
        for alpha in [float(x) for x in range(1,11)]:
            # Mean Latency Value Loop
            for mean in latencyMeanTimes:

                print("Running Test:")
                print("\tDrift Std Deviation: {:.2e}".format(driftStdDev))
                print("\tAlpha: {:.2e}".format(alpha))
                print("\tMean: {:.2e}".format(mean))
                percentCompletion = (((driftStdDev *1e8) - 1) * 10) + (alpha - 1)
                print("\tPercent Completion: {:.2}%".format(percentCompletion))

                directoryPath = "./tmp/{}/{:.2e}_{:.2e}_{:.2e}/".format(time, driftStdDev, alpha, mean)
                if (not os.path.isdir(directoryPath)):
                    os.mkdir(directoryPath)

                freqexpr = "(sum (* {} (normal)))".format(driftStdDev)
                conf = ""

                theta = mean/alpha
                for i in range(2, nodecount + 1):
                    conf += "node{}_offset = {}\n".format(i, i - 1)

                    conf += "node{}_freq = {}\n".format(i, freqexpr)

                    conf += "node{}_delay1 = (gamma {} {})\n".format(i, alpha, theta)
                    conf += "node1_delay{} = (gamma {} {})\n".format(i, alpha, theta)

                conf += "node1_refclock = (* 0 0)\n"


                confFile = open("./tmp/conf", 'w')

                confFile.write(conf)

                confFile.close()


                scriptname = "cephntp.dynamic.test"
                createScript(nodecount, scriptname, directoryPath)

                subprocess.check_call("./{}".format(scriptname), 
                    shell=True)


def configPerfectClocks(nodecount):
    """ Generate client configs """
    conf = ""

    for i in range(1, nodecount + 1):
        conf += "node{}_offset = 0\n".format(i)     
        conf += "node{}_freq = 0\n".format(i)
        conf += "node{}_delay1 = (+ 0 0.001)\n".format(i)
        conf += "node1_delay{} = (+ 0 0.001)\n".format(i)

    conf += "node1_refclock = (* 0 0)\n"

    confFile = open("./tmp/conf", 'w')

    confFile.write(conf)

    confFile.close()


    scriptname = "cephntp.dynamic.test"
    createScript(nodecount, scriptname)

    subprocess.check_call("./{}".format(scriptname), 
        shell=True)

def createScript(nodecount, scriptname, directoryPath = "./tmp/"):

    timeOffsetFilePath = directoryPath + "log.timeoffset" 
    ntpOffsetFilePath = directoryPath + "log.ntp_maxerror"
    ntpMaxErrorFilePath = directoryPath + "log.ntp_offset"
    packetDelaysFilePath = directoryPath + "log.packetdelays"
    print(packetDelaysFilePath)

    script = open("./{}".format(scriptname), 'w')

    script.write("#!/bin/bash\n\n")

    script.write("CLKNETSIM_PATH=..\n")
    script.write(". ../clknetsim.bash\n")

    """ Start clients """
    # use bad clock on root node
    # script.write(
    #     """start_client 1 ntp "server 127.127.1.0" \n"""
    #     )
    # use good clock on root node
    script.write(
       """start_client 1 ntp "server 127.127.28.0" \n"""
       )

    for i in range(2, nodecount + 1):
        script.write("""start_client {} ntp "server {} minpoll 4 maxpoll 6" \n"""
            .format(i, ipaddress.IPv4Address("192.168.123.1")))

    """ Start experiment """
    timeLimit = 20000

    script.write("start_server {} -v 2 -o {} \
-a {} \
-c {} \
-p {} \
-l {} \n".format(nodecount, timeOffsetFilePath, ntpOffsetFilePath, ntpMaxErrorFilePath, packetDelaysFilePath, timeLimit))

    """ Output statistics """
    script.write("cat tmp/stats\n")
    script.write("echo\n")
    script.write("get_stat 'RMS offset'\n")
    script.write("get_stat 'RMS frequency'\n")

    script.close()

    subprocess.check_call("chmod +x ./{}".format(scriptname), 
        shell=True)




def main():

    if (not os.path.isdir("./tmp")):
        os.mkdir("./tmp")

    # config1(100, 0.01, "(+ 1e-6 (sum (* 1e-9 (normal))))", 
    #     "(+ 1e-3 (* 1e-3 (exponential)))")

    # TODO: change offset so each node starts at a different offset
    # config1(10, 0.01, "(sum (* 2e-5 (normal)))", 
    #     "(+ 1e-4 (* 7e-3 (poisson 5)))")
    
    # config1(10, 0.01, "(* 0.0001 (normal))", 
    #     "(+ 1e-4 (* 7e-3 (poisson 5)))")

    # config1(10, 0.01, "(sum (* 1e-8 (normal)))", 
    #     "(+ 1e-3 (* 1e-3 (exponential)))")


    config2(10, 0.01, "(* 6.7e-7 (normal))")
    # config2(10, 0.01, "(0 (* 1e-5 (normal)))")


    # configPerfectClocks(10)
    # config3()


if __name__ == "__main__":
    main()
