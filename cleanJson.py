# -*- coding: utf-8 -*-
"""
Created on 10 March 2015

@author: mattcook
"""
import simplejson
import os
import re

# this is path to file
# uncomment to direct to path of file
# os.chdir(r'/Users/mattcook/Documents')
# this is name of file
fileName = 'timestamps5apr2015v2.json'
# this is name of new clean file to be made
newFileName = 'newtimestamps5apr2015v2.json'

invalidLinesFile = "badlines.txt"

fillerLine = "{\"date\": -1, \"time\": 0.0, \"originTS\": 0.0, \"receiveTS\": 0.0, \"transmitTS\": 0.0, \"destTS\": 0.0}]}"
fillerEndLine = fillerLine + "]\n")
fillerMidLine = fillerLine + ",\n"

def checkForError(f):
    try:
        simplejson.loads(f)
        return True
    except Exception as e:
        return False

def makeJsonLines(line):
    return "[" + line + "\n{\"date\": 1000, \"time\": 1000.235, \"originTS\": 1000.451, \"receiveTS\": 1000.451, \"transmitTS\": 1000.451, \"destTS\": 1000.451}]"
# loop through checking for errors   
lineCounter = 0
firstNode = True
with open(fileName, 'r') as json_data:
    with open(newFileName, 'w') as newJsonData:
        with (open(invalidLinesFile, 'w')) as badlines:
            for line in json_data:
                lineCounter += 1
                # check for the final line in JSON file
                if ("}]}]" in line):
                    if (checkForError(makeJsonLines(line.replace("}]}]", "},")))):
                        newJsonData.write(line)
                    else:
                        print "Error in line", lineCounter
                        print line
                        newJsonData.write(fillerEndLine)
                # check for the end of one node
                elif ("}]}," in line):
                    line = line.replace("}]}", "}")
                    if (checkForError(makeJsonLines(line))):
                        newJsonData.write(line)
                    else:
                        print "Error in line", lineCounter
                        print line
                        newJsonData.write(fillerMidLine)
                # check for first line in node data
                elif ("\"node\"" in line):
                    # make sure we don't put an invalid line for the very first one
                    if (firstNode):
                        firstNode = False
                    else:
                        newJsonData.write(fillerMidLine)
                    line = re.sub(r'"entries":\[.+', r'"entries":[', line)
                    newJsonData.write(line)
                # check if this line is valid
                elif (checkForError(makeJsonLines(line))):
                    newJsonData.write(line)
                # if not, throw away this line
                else:
                    #print "Error in line", lineCounter
                    #print line
                    badlines.write(line)
                    badlines.write("\n")
print "Done Checking!"
