# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 17:55:06 2019

@author: omr-w
"""

import serial.tools.list_ports as list_ports
import argparse
from os import sys


def isValidPort(selection):
    valid_ports = [ comport.device for comport in list_ports.comports()];
    if selection not in valid_ports:
        print("Value error: invalid port", selection, "choosen. Abort.");
        return False;

    return True;

def listAvailablePorts(enable_print):
    if ( enable_print ):
        print("Available serial ports with device description:");
        [ print(" ", comport.device, ":", comport.description) for comport in list_ports.comports()];
    return [ "{} - {}".format(comport.device, comport.description) for comport in list_ports.comports()];

class ShowPortsAction(argparse.Action):
    def __init__(self, nargs=0, **kwargs):
        if nargs != 0:
            raise ValueError("This is a flag and takes no arguments")
        super(ShowPortsAction, self).__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True);
        listAvailablePorts();
        #[ print(comport.device, "description:", comport.description, "name:", comport.name, "hwid:", comport.hwid, "vid:", comport.vid, "pid:", comport.pid, "serial_number:", comport.serial_number, "location:", comport.location, "manufacturer:", comport.manufacturer, "product:", comport.product, "inferface:", comport.interface) for comport in list_ports.comports()];

        if namespace.serialPort != None:
            if not isValidPort(namespace.serialPort):
                sys.exit()
        else:
            sys.exit()


#Not used for now as it was not tested enough
class validPortAction(argparse.Action):
    def __init__(self, nargs=1, **kwargs):
        if nargs != 1:
            raise ValueError("a port needs to be specified.")
        super(validPortAction, self).__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values[0])
        if not isValidPort(values[0]):
            listAvailablePorts();

            sys.exit()
