#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

"""##########################################################################
#                               CFGtoCSV                                    #
#   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   #
#                               PURPOSE                                     #
#                                                                           #
#   This Python script makes a .csv archive with the hosts and services     #
#   of Nagios .cfg files. It also generates Nagios .cfg files collecting    #
#   data of a .csv file. This .csv files can be used as backup of Nagios    #
#   .cfg files and/or generating Nagios .cfg files more easy than           #
#   creating them manually, specially with a large amount of Hosts          #
#   and/or services.                                                        #
#                                                                           #
#   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   #
#                               LICENSE                                     #
#                                                                           #
#   Copyright 2016 Albert Casas Granados                                    #
#   albert.casasgranados@gmail.com                                          #
#   09/03/2016                                                              #
#                                                                           #
#   This program is free software: you can redistribute it and/or modify    #
#   it under the terms of the GNU General Public License as published by    #
#   the Free Software Foundation, either version 3 of the License, or       #
#   (at your option) any later version.                                     #
#                                                                           #
#   This program is distributed in the hope that it will be useful,         #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#   GNU General Public License for more details.                            #
#                                                                           #
#   You should have received a copy of the GNU General Public License       #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.   #
#                                                                           #
##########################################################################"""

from optparse import OptionParser
import subprocess, os.path, csv

version = "0.18"
release = "17/03/2016"

def cfg2csv(cfgFile, debug):
    """ From a Nagios .cfg file (function input) returns a .csv file with
    the same name as the input file with all data of hosts and/or services
    stored within. If debug is not 0, debug messages should be printed. """
    if debug:
        print "cfg2csv function is selected\n"

        cfgReader = open(cfgFile, 'r')
        if debug:
            print cfgReader
        cfgContent = cfgReader.readlines()
        csvFile = open(cfgFile[:-3]+"csv", 'w')
        if debug:
            print csvFile
        fieldNames = ['Template', 'Hostname', 'Alias', 'IP', 'Hostgroups', 'Contactgroups', 'NotificationInterval', 'CheckInterval', 'RetryCheckInterval', 'SNMP', 'Ping', 'Uptime', 'Stack', 'Interface']
        csvWriter = csv.DictWriter(csvFile, fieldnames = fieldNames, delimiter = ';', lineterminator='\n')
        if debug:
            print csvWriter
        csvWriter.writeheader()
        
        hostCount = 0
        serviceCount = 0
        
        #print cfgContent
        
        row = {'Template': "", 'Hostname': "", 'Alias': "", 'IP': "", 'Hostgroups': "", 'Contactgroups': "", 'NotificationInterval': "", 'CheckInterval': "", 'RetryCheckInterval': "", 'SNMP': "", 'Ping': "", 'Uptime': "", 'Stack': "", 'Interface': ""}
        lineEnd = ""
        hostContactsCheck = False
        NotificationIntervalCheck = False
        CheckIntervalCheck = False
        RetryCheckIntervalCheck = False
        pingCheck = False
        uptimeCheck = False
        stackCheck = False
        ifCount = 0
        for line in cfgContent:
            #print line[42:]
            
            if line == "define host{\n":
                hostCount += 1               
            elif line == "define service{\n":
                serviceCount += 1
            elif (line[0:8] == "    use ") and lineEnd == "":
                row['Template'] = line[8:-1]
                if debug:
                    print "\n---\nDetected host template: %s" % row['Template']
            elif (line[0:14] == "    host_name ") and lineEnd == "":
                row['Hostname'] = line[14:-1]
                lineEnd = "#   Host %s End\n" % row['Hostname']
                if debug:
                    print "Detected Host: %s" % row['Hostname']
                    print "Line end set: %s" % lineEnd[0:-1]
            elif (line[0:10] == "    alias ") and lineEnd != "":
                row['Alias'] = line[10:-1]
                if debug:
                    print "Detected host Alias: %s" % row['Alias']
            elif (line[0:12] == "    address ") and lineEnd != "":
                row['IP'] = line[12:-1]
                if debug:
                    print "Detected host IP: %s" % row['IP']
            elif (line[0:15] == "    hostgroups ") and lineEnd != "":
                row['Hostgroups'] = line[15:-1]
                if debug:
                    print "Detected Hostgroups IP: %s" % row['Hostgroups']
            elif (line[0:19] == "    contact_groups ") and lineEnd != "" and hostContactsCheck == False:
                row['Contactgroups'] = line[19:-1]
                hostContactsCheck = True
                if debug:
                    print "Detected Contactgroups IP: %s" % row['Contactgroups']
            elif (line[0:26] == "    notification_interval ") and lineEnd != "" and NotificationIntervalCheck == False:
                row['NotificationInterval'] = line[26:-1]
                NotificationIntervalCheck = True
                if debug:
                    print "Detected NotificationInterval: %s" % row['NotificationInterval']
            elif (line[0:26] == "    normal_check_interval ") and lineEnd != "" and CheckIntervalCheck == False:
                row['CheckInterval'] = line[26:-1]
                CheckIntervalCheck = True
                if debug:
                    print "Detected CheckInterval: %s" % row['CheckInterval']
            elif (line[0:25] == "    retry_check_interval ") and lineEnd != "" and RetryCheckIntervalCheck == False:
                row['RetryCheckInterval'] = line[25:-1]
                RetryCheckIntervalCheck = True
                if debug:
                    print "Detected RetryCheckInterval: %s" % row['RetryCheckInterval']
            elif (line[0:20] == "    #SNMP_community ") and lineEnd != "":
                row['SNMP'] = line[20:-1]
                if debug:
                    print "Detected SNMP: %s" % row['SNMP']
            elif (line[0:29] == "    check_command check_ping!") and lineEnd != "":
                row['Ping'] = "yes"
                pingCheck = True
                if debug:
                    print "Detected Service: Ping"
            elif (line[0:29] == "    check_command check_snmp!") and (line[42:] == 'sysUpTime.0\n')and lineEnd != "":
                row['Uptime'] = "yes"
                uptimeCheck = True
                if debug:
                    print "Detected Service: Uptime"
            elif (line[0:30] == "    check_command check_stack!") and lineEnd != "":
                row['Stack'] = "yes"
                stackCheck = True
                if debug:
                    print "Detected Service: Stack"
            if (line[0:36] == "    service_description Interface - ") and lineEnd != "":
                if ifCount == 0:
                    ifLine = line[36:-1]
                    if debug:
                        print "Detected Interface: %s" % ifLine
                    ifLine = ifLine.split(' - ')
                    row['Interface'] = ifLine[0]+':'+ifLine[1]
                    ifCount += 1
                elif ifCount >= 1:
                    ifLine = line[36:-1]
                    if debug:
                        print "Detected Interface: %s" % ifLine
                    ifLine = ifLine.split(' - ')
                    row['Interface'] = row['Interface']+','+ifLine[0]+':'+ifLine[1]
                    ifCount += 1
                
            elif line == lineEnd:
                if pingCheck == False:
                    row['Ping'] = "no"
                if uptimeCheck == False:
                    row['Uptime'] = "no"
                if stackCheck == False:
                    row['Stack'] = "no"
                if debug and ifCount >= 1:
                    print "Detected Interfaces: %s" % ifCount
                csvWriter.writerow(row) 
                lineEnd = ""
                hostContactsCheck = False
                NotificationIntervalCheck = False
                CheckIntervalCheck = False
                RetryCheckIntervalCheck = False
                pingCheck = False
                uptimeCheck = False
                stackCheck = False
                ifCount = 0
                if debug:
                    print "Detected host end: %s" % line
                    print "Writed: %s\n---\n" % row
                row = {'Template': "", 'Hostname': "", 'Alias': "", 'IP': "", 'Hostgroups': "", 'Contactgroups': "", 'NotificationInterval': "", 'CheckInterval': "", 'RetryCheckInterval': "", 'SNMP': "", 'Ping': "", 'Uptime': "", 'Stack': "", 'Interface': ""}
        
        print hostCount, serviceCount
        
        cfgReader.close()
        if debug:
            print cfgReader
        csvFile.close()
        if debug:
            print csvFile
    
    
    return cfgFile
# END cfg2csv    

def csv2cfg(csvFile, debug, version, release):
    """ From a .csv file (function input) returns a Nagios .cfg file with
    the same name as the input file with all of the hosts and/or services
    listed in the input .csv file. If debug is not 0, debug messages 
    should be printed. """
    if debug:
        print "csv2cfg function is selected\n"
    
    csvContent = open(csvFile, 'r')
    if debug:
        print csvContent        
    csvReader = csv.DictReader(csvContent, delimiter = ';')
    if debug:
        print csvReader
    cfgWrite = open(csvFile[:-3]+"cfg", 'w')
    if debug:
        print cfgWrite
        print "\n"
    cfgWrite.write(str("""#########################################################################
#           Nagios Configuration File generated by CFGtoCSV             #
#   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   #
#   CFGtoCSV version: %s - %s                                 #
#                                                                       #
#########################################################################

""")% (version, release))
    
    hostCount = 0
    for row in csvReader:
        hostCount += 1
        cfgWrite.write(str("""#=======================================================================#  
#   %s - %s - %s            
#   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   #
define host{
    use %s
    host_name %s
    alias %s
    address %s
    hostgroups %s
    contact_groups %s
    notification_interval %s
    normal_check_interval %s
    retry_check_interval %s
    #SNMP_community %s
}

#   %s - Services""") % (hostCount, row['Hostname'], row['IP'], row['Template'], row['Hostname'], row['Alias'], row['IP'], row['Hostgroups'], row['Contactgroups'], row['NotificationInterval'], row['CheckInterval'], row['RetryCheckInterval'], row['SNMP'], row['Hostname']))

        if row['Ping'] == "yes":
            cfgWrite.write(str("""
define service{
    use generic-service
    host_name %s
    service_description Ping
    servicegroups sg-ping
    contact_groups %s
    check_command check_ping!3000.0,80%%!5000.0,100%%
    notification_interval %s
    normal_check_interval %s
    retry_check_interval %s
}
""") % (row['Hostname'], row['Contactgroups'], row['NotificationInterval'], row['CheckInterval'], row['RetryCheckInterval']))

        if row['Uptime'] == "yes":
            cfgWrite.write(str("""
define service{
    use generic-service
    host_name %s
    service_description Uptime
    servicegroups sg-uptime
    contact_groups %s
    check_command check_snmp!-C %s -o sysUpTime.0
    notification_interval %s
    normal_check_interval %s
    retry_check_interval %s
}
""") % (row['Hostname'], row['Contactgroups'], row['SNMP'], row['NotificationInterval'], row['CheckInterval'], row['RetryCheckInterval']))

        if row['Stack'] == "yes":
            cfgWrite.write(str("""
define service{
    use generic-service
    host_name %s
    service_description Stack
    servicegroups sg-stack
    contact_groups %s
    check_command check_stack!-H %s -C %s
    notification_interval %s
    normal_check_interval %s
    retry_check_interval %s
}
""") % (row['Hostname'], row['Contactgroups'], row['IP'], row['SNMP'], row['NotificationInterval'], row['CheckInterval'], row['RetryCheckInterval']))

        if row['Interface'] != "":
            interfaces = row['Interface'].split(',')
            for line in interfaces:
                line = line.split(':')
                interface = line[0]
                interfaceAlias = " - "+line[1]
                cfgWrite.write(str("""
define service{
    use generic-service
    host_name %s
    service_description Interface - %s%s
    servicegroups sg-if
    contact_groups %s
    check_command check_if!%s!%s!%s
    notification_interval %s
    normal_check_interval %s
    retry_check_interval %s
}
""") % (row['Hostname'], interface, interfaceAlias, row['Contactgroups'], row['IP'], row['SNMP'], interface, row['NotificationInterval'], row['CheckInterval'], row['RetryCheckInterval']))

        if (row['Ping'] == "no") and (row['Uptime'] == "no") and (row['Stack'] == "no") and (row['Interface'] == ""):
            print ("Host %s: %s has not any service.") % (hostCount, row['Hostname'])
            csvContent.close()
            if debug:
                print ("\nProcessed hosts: %s\n") % hostCount
                print csvContent
            cfgWrite.close()
            if debug:
                print cfgWrite
                print "\n"
            os.remove(csvFile[:-3]+"cfg")
            break

        cfgWrite.write(str(("#   Host %s End\n\n") % row['Hostname']))
        if debug:
            print str(row)
                
    csvContent.close()
    if debug:
        print ("\nProcessed hosts: %s\n") % hostCount
        print csvContent
    cfgWrite.close()
    if debug:
        print cfgWrite
        print "\n"
    
    return csvFile
# END csv2cfg
    
parser = OptionParser(description="Translates Nagios .cfg files to .csv files and backwards.")

parser.add_option("-d", "--debug", action = "store_true", help = "Displays debug info.")
parser.add_option("-f", "--file", help = "File to translate.")
(options, args) = parser.parse_args()

if options.debug:
    subprocess.call(["clear"], shell=True)
    print ("Debug messages activated\nVersion: %s\nRelease: %s\n\nParameters: %s\n") % (version, release, options)
else:
    debug = False

if options.file is None:
	parser.error ("Insert a valid filename to convert. (-f FILENAME --host FILENAME)")
elif options.file[-4:] != ".csv" and options.file[-4:] != ".cfg":
    parser.error ("File format is not .csv or .cfg. Enter a valid format.")
elif options.file[-4:] == ".cfg":
    if os.path.isfile(options.file): 
        cfg2csv(options.file,options.debug)
    else:
        parser.error ("File not found.")
elif options.file[-4:] == ".csv":
    if os.path.isfile(options.file): 
        csv2cfg(options.file,options.debug,version,release)
    else:
        parser.error ("File not found.")
else:
    parser.error ("Error with source file fetching")
