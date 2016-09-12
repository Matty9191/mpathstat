## Overview

The mpathstat utility provides device mapper statistics for each mapper device as well as the SCSI block devices that represent the paths to this device. Here is some sample output to illustrate the utility in action:

## Usage:
<pre>
$ mpathstat.py
 Device Name                                  Reads     Writes    KBytesR/S  KBytesW/S  Await   
 mpatha                                       8.00      0.00      4096.00    0.00       4.88    
 |- sdcl                                      1.00      0.00      512.00     0.00       4.00    
 |- sdfy                                      1.00      0.00      512.00     0.00       5.00    
 |- sdava                                     1.00      0.00      512.00     0.00       7.00    
 |- sdayn                                     1.00      0.00      512.00     0.00       4.00    
 |- sdtf                                      1.00      0.00      512.00     0.00       5.00    
 |- sdws                                      1.00      0.00      512.00     0.00       4.00    
 |- sdaas                                     1.00      0.00      512.00     0.00       5.00    
 |- sdaef                                     1.00      0.00      512.00     0.00       5.00    
 .......
</pre>

## Feedback, commits and comments

All feedback is welcomed.

