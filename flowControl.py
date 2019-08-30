# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 18:01:36 2019

@author: omr-w
"""

import argparse
import serial_utils as sutils
from main_window import mainWindow as mW
from start_window import startWindow as sW

if ( '__main__' == __name__ ):
    argp = argparse.ArgumentParser()
    argp.add_argument('-p', '--serialPort', default='', action='store', type=str, help='Specifies used serial port');
    argp.add_argument('-br', '--baudrate', default=9600, action='store', type=int, help='Specifies used baudrate');
    argp.add_argument('-s','--show', action=sutils.ShowPortsAction, help='Show available Ports', )
    args = argp.parse_args()

    if args.serialPort == '':
        startWindow = sW();
        args.serialPort, args.baudrate = startWindow.run();
        if ( args.serialPort == 'Exit' ):
            sys.exit()
    else:
        print("open", args.serialPort, " with baudrate", args.baudrate);
        #serComm = sc(args.serialPort, 9600);

    mainWindow = mW(args.serialPort, args.baudrate);
    mainWindow.run()
