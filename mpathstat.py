#!/usr/bin/env python
#
# Program: Device mapper statistics utility <mpathstat.py>
#
# Author: Matty < matty91 at gmail dot com >
#
# Current Version: 1.1
#
# Revision History:
#
# Version 1.1
#     Original release
#
# Last Updated: 10-24-2016
#
# Purpose: Displays I/O statistics for each device mapper device as well as the
#          individual block devices that represent each path to that mapper device.
#
# Example:
# $ mpathstat.py
# Device Name                                  Reads     Writes    KBytesR/S  KBytesW/S  Await   
# mpatha                                       8.00      0.00      4096.00    0.00       4.88    
# |- sdcl                                      1.00      0.00      512.00     0.00       4.00    
# |- sdfy                                      1.00      0.00      512.00     0.00       5.00    
# |- sdava                                     1.00      0.00      512.00     0.00       7.00    
# |- sdayn                                     1.00      0.00      512.00     0.00       4.00    
# |- sdtf                                      1.00      0.00      512.00     0.00       5.00    
# |- sdws                                      1.00      0.00      512.00     0.00       4.00    
# |- sdaas                                     1.00      0.00      512.00     0.00       5.00    
# |- sdaef                                     1.00      0.00      512.00     0.00       5.00    
# .......
#
# Assumptions: Assumes iostat output will contain block devices with "sd" in their name and mapper 
# devices will have dm in their name. It also assumes that the multipath output will keep the dm-
# device on the same line as the mpath devices. Furthermore it assumes that block devices in the
# multipath output will start with either a "|-" or a "`-".
#
# License:
#   This program is free software; you can redistribute it and/or modify it   
#   under the terms of the GNU General Public License as published by the     
#   Free Software Foundation; either version 2, or (at your option) any
#   later version.
# 
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


import sys
import signal
import collections
import subprocess

# Create two collections. One for mapper devices 
# and another for block devices that map to the
# mapper devices.
dmname = ""
blockdevice = ""
blockdevices = collections.defaultdict(dict)
mapperdevices = collections.defaultdict(dict)
multipath = "/sbin/multipath -ll"
iostat = "/usr/bin/iostat -xkyz 1 1"


# Catch SIGINT so we can exit with grace.
def gexit(signum, frame):
    """
       Function to call if a SIGINT is received
    """
    sys.exit(1)


def initcollections():
    """
       Initialize the read/write metrics to 0
    """
    for mdev in mapperdevices:
        mapperdevices[mdev]['await'] = 0
        mapperdevices[mdev]['reads'] = 0
        mapperdevices[mdev]['writes'] = 0
        mapperdevices[mdev]['bytes_read'] = 0
        mapperdevices[mdev]['bytes_written'] = 0
	
    for bdev in blockdevices:
        blockdevices[bdev]['await'] = 0
        blockdevices[bdev]['reads'] = 0
        blockdevices[bdev]['writes'] = 0
        blockdevices[bdev]['bytes_read'] = 0
        blockdevices[bdev]['bytes_written'] = 0

def parse_devs():
    """
       Parse multipath -ll to get the list of mapper and sd devices
    """
    signal.signal(signal.SIGINT, gexit)

    try:
        subproc = subprocess.Popen(multipath, shell=True, stdout=subprocess.PIPE)
    except OSError:
        print "Error opening the multipath utility."
        print "Command executed: " + multipath
        sys.exit(1)

    # Check the string to see if it contains "dm-". If it does we located
    # a device mapper entry that we need to save. If we don't encounter a
    # dm line we need to locate the block devices that are part of the
    # mapper device we saved. These entries contain "|-" or "`-".
    for line in subproc.stdout.readlines():
        if ' dm-' in line :
            dmname = line.split()[2]
            mapperdevices[dmname]['pretty_name'] = line.split()[0]
        elif ' |-' in line or ' `-' in line :
            blockdevices[line.split()[-5]]['mapper_device'] = dmname

    # Set the counters to zero.
    initcollections()


def process_io_stats():
    """
       Iterates over iostat data and updates the device mapper array
       Iostat format:
       Device:         rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await  svctm  %util
       sda               0.00     1.00    0.00    3.00     0.00    12.00     8.00     0.00    0.00   0.00   0.00
    """

    # Iterate over the iostat output and update the counters
    while True:
        print   "%-43s  %-8s  %-8s  %-9s  %-9s  %-8s" % ("Device Name", "Reads", "Writes", 
                                                     "KBytesR/S", "KBytesW/S", "Await")

        try:
            subproc = subprocess.Popen(iostat, shell=True, stdout=subprocess.PIPE)
        except OSError:
            print "Error opening the iostat utility."
            print "Command executed: " + iostat
            sys.exit(1)

        for line in subproc.stdout.readlines():
            if "sd" in line:
                blockdev = line.split()[0]
                if blockdev in blockdevices:
                    blockdevices[blockdev]['await'] = float(line.split()[9])
                    blockdevices[blockdev]['reads'] = float(line.split()[3])
                    blockdevices[blockdev]['writes'] = float(line.split()[4])
                    blockdevices[blockdev]['bytes_read'] = float(line.split()[5])
                    blockdevices[blockdev]['bytes_written'] = float(line.split()[6])
            elif "dm" in line:
                mapperdev = line.split()[0]
                if mapperdev in mapperdevices:
                    mapperdevices[mapperdev]['await'] = float(line.split()[9])
                    mapperdevices[mapperdev]['reads'] = float(line.split()[3])
                    mapperdevices[mapperdev]['writes'] = float(line.split()[4])
                    mapperdevices[mapperdev]['bytes_read'] = float(line.split()[5])
                    mapperdevices[mapperdev]['bytes_written'] = float(line.split()[6])

        for mdev in mapperdevices:
            if mapperdevices[mdev]['reads'] > 0 or mapperdevices[mdev]['writes'] > 0:
                print   "%-43s  %-8.2f  %-8.2f  %-9.2f  %-9.2f  %-8.2f" % (mapperdevices[mdev]['pretty_name'],
                                                                           mapperdevices[mdev]['reads'],
                                                                           mapperdevices[mdev]['writes'],
                                                                           mapperdevices[mdev]['bytes_read'],
                                                                           mapperdevices[mdev]['bytes_written'],
                                                                           mapperdevices[mdev]['await'])

                for bdev in blockdevices:
                    if blockdevices[bdev]["mapper_device"] == mdev:
                        print   "|- %-40s  %-8.2f  %-8.2f  %-9.2f  %-9.2f  %-8.2f" % (bdev,
                                                                            blockdevices[bdev]['reads'],
                                                                            blockdevices[bdev]['writes'],
                                                                            blockdevices[bdev]['bytes_read'],
                                                                            blockdevices[bdev]['bytes_written'],
                                                                            blockdevices[bdev]['await'])

    # Reset the counters to zero
    initcollections()
    print ""


def main():
    """
       Main code block
    """
    parse_devs()
    process_io_stats()


if __name__ == "__main__":
    main()
