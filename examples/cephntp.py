#!/usr/bin/env python3

import os
import ipaddress
import subprocess
import datetime
import math


# generalConfig creates a configuration file for a clknetsim run and runs the
# simulation using the configuration file. The user can specify:
#   1) The number of nodes
#   2) The clknetsim expression for the frequency offsets of the nodes
#   3) The clknetsim expression for a packet's delay to the 1st node (probably your NTP server)
#   4) The clknetsim expression for a packet's delay from the 1st node (probably your NTP server)
def generalConfig(nodecount, freqexpr, delayexprup, delayexprdown = ""):
    """ Generate client configs """

    # The text of the configuration file.
    conf = ""

    # For each node that the user specifies, we specify certain characteristics
    for i in range(1, nodecount + 1):
        # This specifies the initial offset of the clock
        conf += "node{}_offset = {}\n".format(i, i - 1)
        
        # For non-server nodes, we specify the clknetsim expression to use for
        # the frequency change of the node
        if (i != 1):
            conf += "node{}_freq = {}\n".format(i, freqexpr)

        # We specify the expression for packet delays to the server.
        conf += "node{}_delay1 = {}\n".format(i, delayexprup)

        # We specify the expression for packet delays from the server. If a 
        # different expression is not specified, then it just uses the expression
        # for packets to the server.
        if (delayexprdown != ""):
            conf += "node1_delay{} = {}\n".format(i, delayexprdown)
        else:
            conf += "node1_delay{} = {}\n".format(i, delayexprup)

    confFile = open("./tmp/conf", 'w')

    confFile.write(conf)

    confFile.close()


    scriptname = "cephntp.dynamic.test"
    createScript(nodecount, scriptname)

    subprocess.check_call("./{}".format(scriptname), 
        shell=True)

# realLatencyConfig is similar to generalConfig, except packet latency
# values are drawn from data drawn from a real test cluster. The user can specify:
#   1) The number of nodes
#   2) The clknetsim expression for the frequency of the nodes
#   3) Directory where latency data is stored
def realLatencyConfig(nodecount, freqexpr, latencyValuesDir = "../latencydata"):
    """ Generate client configs """

    # The text of the configuration file.
    conf = ""

    # For each node that the user specifies, we specify certain characteristics
    for i in range(1, nodecount + 1):
        # This specifies the initial offset of the clock
        conf += "node{}_offset = {}\n".format(i, i - 1)

        # For non-server nodes, we specify the clknetsim expression to use for
        # the frequency change of the node 
        if (i != 1):
            conf += "node{}_freq = {}\n".format(i, freqexpr)

        # We specify the latency values for the packets to the server.
        conf += "node{}_delay1 = (file \"{}/latencyValues{}.txt\")\n".format(i, latencyValuesDir, i)
        # we use a different latency file for the return trip than for the initial trip
        conf += "node1_delay{} = (file \"{}/latencyValues{}.txt\")\n".format(i, latencyValuesDir, i + (nodecount - 1))

    confFile = open("./tmp/conf", 'w')

    confFile.write(conf)

    confFile.close()


    scriptname = "cephntp.dynamic.test"
    createScript(nodecount, scriptname)

    subprocess.check_call("./{}".format(scriptname), 
        shell=True)

# multiRunConfig varies different parameters and runs a simulation for each
# configuration. The parameters that are varied are the standard deviation in
# the clock drift, and two parameters in the gamma distribution modeling 
# packet latency (the mean and the alpha parameter).
def multiRunConfig():
    """ Generate client configs """
    # The number of nodes in our simulation. We only run this with two nodes (a
    # server and a client) because a) a node's behavior isn't dependent on the 
    # other nodes in the cluster and, therefore, we don't need other nodes to
    # see how nodes; and b) since 3000 simulations are being run, the script
    # takes long enough as is.
    nodecount = 2

    # The current date and time is used to create a unique directory for the
    # output. This way, the user can run the simulations multiple times without
    # worrying that previous output has been overwritten.
    time = str(datetime.datetime.now()).replace(" ", "_")

    # We create the directories if it hasn't already been made.
    if (not os.path.isdir("./tmp")):
        os.mkdir("./tmp")
    os.mkdir("./tmp/{}".format(time))

    # This is the latency mean times we are generating for our simulations. 
    # We generate them on a log scale, since lower mean values are more typical
    # for a cluster and, therefore, we'd like more definition in that area. 
    # Currently, we generate values from 0.01ms to 10ms
    latencyMeanTimes = [10**((float(x)/10.0) - 5) for x in range(31)]

    # Clock Drift Std Deviation Loop
    for driftStdDev in [1e-8*float(x) for x in range(1,11)]:
        # Latency Alpha Value Loop
        for alpha in [float(x) for x in range(1,11)]:
            # Mean Latency Value Loop
            for mean in latencyMeanTimes:

                # Progress Output
                print("Running Test:")
                print("\tDrift Std Deviation: {:.2e}".format(driftStdDev))
                print("\tAlpha: {:.2e}".format(alpha))
                print("\tMean: {:.2e}".format(mean))
                percentCompletion = (((driftStdDev *1e8) - 1) * 10) + (alpha - 1)
                print("\tPercent Completion: {:.2}%".format(percentCompletion))

                # We create a directory path for the output from each simulation
                # run.
                directoryPath = "./tmp/{}/{:.2e}_{:.2e}_{:.2e}/".format(time, driftStdDev, alpha, mean)
                if (not os.path.isdir(directoryPath)):
                    os.mkdir(directoryPath)

                # Here, we use the driftStdDev when setting the frequency of
                # the node.
                freqexpr = "(sum (* {} (normal)))".format(driftStdDev)

                # The text of the configuration file.
                conf = ""

                # We need the theta value to generate our gamma distribution.
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



# configPerfectClocks configures the nodes in the cluster to have perfect clocks
# i.e. ones that are never out of sync. It's used to determine how NTP handles
# this peculiar scenario.
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


# (FIXME: You wrote this; could you comment it?)
def createScript(nodecount, scriptname, directoryPath = "./tmp/"):
    """
    Put together other parts of the scripts and kick things off.

    nodecount:      How many nodes in the simulation
    scriptname:     What to call the script
    directoryPath:  Where to put the script
    """

    # Where to stick output files
    timeOffsetFilePath = directoryPath + "log.timeoffset" 
    ntpOffsetFilePath = directoryPath + "log.ntp_maxerror"
    ntpMaxErrorFilePath = directoryPath + "log.ntp_offset"
    packetDelaysFilePath = directoryPath + "log.packetdelays"
    print(packetDelaysFilePath)

    # Open the script file for writing
    script = open("./{}".format(scriptname), 'w')

    # Fill out some header stuff
    script.write("#!/bin/bash\n\n")

    script.write("CLKNETSIM_PATH=..\n")
    script.write(". ../clknetsim.bash\n")


    """ 
    NTP parameters set clock types as variations on 127.127.xx.0.
    We can say that NTP should trust its own clock (and not sync with
    anyone else) with 127.127.1.0. Clknetsim provides a SHM type virtual
    clock however that we can make use of if we would like to at
    127.127.28.0. This clock is configured using the 'refclock' properties
    of a node.
    """

    # use bad clock on root node
    # script.write(
    #     """start_client 1 ntp "server 127.127.1.0" \n"""
    #     )
    # use good clock on root node
    script.write(
       """start_client 1 ntp "server 127.127.28.0" \n"""
       )

    # Tell each client how to start
    for i in range(2, nodecount + 1):
        script.write("""start_client {} ntp "server {} minpoll 4 maxpoll 6" \n"""
            .format(i, ipaddress.IPv4Address("192.168.123.1")))

    # Set how long the experiment should run
    timeLimit = 20000

    # Start the NTP server
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

    # Make sure all of the permissions are set up appropriately
    subprocess.check_call("chmod +x ./{}".format(scriptname), 
        shell=True)




def main():

    if (not os.path.isdir("./tmp")):
        os.mkdir("./tmp")

    # config(100, 0.01, "(+ 1e-6 (sum (* 1e-9 (normal))))", 
    #     "(+ 1e-3 (* 1e-3 (exponential)))")

    # config(10, 0.01, "(sum (* 2e-5 (normal)))", 
    #     "(+ 1e-4 (* 7e-3 (poisson 5)))")
    
    # config(10, 0.01, "(* 0.0001 (normal))", 
    #     "(+ 1e-4 (* 7e-3 (poisson 5)))")

    # config(10, 0.01, "(sum (* 1e-8 (normal)))", 
    #     "(+ 1e-3 (* 1e-3 (exponential)))")


    realLatencyConfig(10, 0.01, "(* 6.7e-7 (normal))")
    # realLatencyConfig(10, 0.01, "(0 (* 1e-5 (normal)))")


    # configPerfectClocks(10)
    # multiRunConfig()


if __name__ == "__main__":
    main()
