"""
Created on Wed Jul 31 20:58:16 2019

@author: omr-w
"""

import PySimpleGUI as sg
from serial_comm import serial_communication as sc
import serial_utils as sutils
import time
import signal
import shutil
import os

class startWindow(object):
    """ Start Window for the regulator """

    def __init__(self):
        self.serial_initialized = 0;
        self.baudrate = None
        self.port = None

        self.refresh_serial_port_list();
        self.setup();

    def refresh_serial_port_list(self):
        self.ports = ['Refresh port list']
        self.ports += sutils.listAvailablePorts(0)

        self.menu_def = [ ['File', ['Change Output File To...', 'Exit',]],
                     ['Help', 'About'], ]

    def setup(self):
        padding = ((0,0),0)
        colpadding = ((0,0),8)
        self.maxDisplayedPorts = 4

        ports = [ self.ports[i] if ( i < (len(self.ports)) ) else 'None' for i in range(1,1+self.maxDisplayedPorts) ]
        framePort = [ [ sg.Radio(None, "ports", enable_events=True, key="port{:d}".format(i) ), sg.Text("{}".format(p), size=(40,1), pad=padding, key="port{:d}Text".format(i) ) ] for i, p in enumerate(ports) ]

        baudrates = [ 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000 ]
        baudlist = [ [ sg.Radio(" {:d}".format(br), "baudrate", enable_events=True, key="baudrate{:d}".format(cnt), size=(7,1)) ] for cnt, br in enumerate(baudrates) ]
        baudlist.append( [ sg.Radio("", "baudrate", enable_events=True, key="baudrateCustom", pad=((5,1),(2,0)) ),
                            sg.InputText("", size=(7,1), key="baudrateCustomValue", pad=((0,20),(0,0)) ) ] )

        colBaud1  = baudlist[:len(baudlist)>>1]
        colBaud2  = baudlist[len(baudlist)>>1:]
        frameBaud = [ [ sg.Column(colBaud1, pad=((0,48),8)), sg.Column(colBaud2, pad=((0,42),8)) ] ]

        colLeft =   [ [ sg.Frame("Serial Port", framePort, size=(20,20)), ],
                      [ sg.Frame("Baudrate", frameBaud, size=(20,20)), ],
                        ]

        colRight=   [ [ sg.Multiline(size=(64,32), key='print_area', autoscroll=True, disabled=True), ], ]

        layout = [  [ sg.Menu(self.menu_def, key='menu') ],
                    [ sg.Text("Please select the serial port to be used."), ],
                    [ sg.Column(colLeft, pad=colpadding), sg.Column(colRight, pad=colpadding), ],
                      ]

        self.window = sg.Window('Choose your serial port', layout, auto_size_text=True, default_element_size=(40, 1))

    def startSerial(self, serialPort, baudrate):
        try:
            print("Open serial port", serialPort)
            self.serialComm = sc(serialPort, baudrate);

            self.serial_initialized = True
            #clear current buffer, to avoid problems with possible corrupt data
            self.serialComm.clearBuffer();
            print("serial initializes")
        except Exception as e:
            self.showWarning("Wrong serial port", "The choosen serial port does not respond, please choose another.")
            self.serialComm = None
            self.serial_initialized = False

    def refresh_serial_radio_list(self):
        self.refresh_serial_port_list()
        ports = [ self.ports[i] if ( i < (len(self.ports)) ) else 'None' for i in range(1,1+self.maxDisplayedPorts) ]

        for i, p in enumerate(ports):
            self.window.Element("port{:d}Text".format(i)).Update(value="{}".format(p))

    def run(self):
        while True:
            event, values  = self.window.Read(timeout=250)
            if ( 0 > self.processWindowInput(event, values) ):
                break;

            self.refresh_serial_radio_list();

            if ( self.serial_initialized ):
                try:
                    newText = self.serialComm.ser.read(50)
                    if ( newText != b'' ):
                        try:
                            newText = newText.decode('ascii')
                        except:
                            #do nothing, if could not be decoded
                            newText

                        displayedText = self.window.Element('print_area').DefaultText + str(newText)
                        self.window.Element('print_area').Update(value=displayedText)
                except:
                    print("serial read gone wrong")

        #if ( self.serial_initialized ):
            #self.serialComm.closeComm();
        self.window.Close()
        return (self.port, self.baudrate)

    def try_open_port(self):
        if ( self.baudrate == None or self.port == None ):
            self.serialComm = None
            self.serial_initialized = False
            return;

        newText = self.window.Element('print_area').DefaultText + "\n> Try open port {} {}...\n".format(self.port, self.baudrate)
        self.window.Element('print_area').Update(value=newText)
        print("try open port", self.port, self.baudrate)

        try:
            self.serialComm = sc(self.port, self.baudrate);

            self.serial_initialized = True
            #clear current buffer, to avoid problems with possible corrupt data
            self.serialComm.clearBuffer();
            print("serial initializes")
        except Exception as e:
            print("Wrong serial port", "The choosen serial port does not respond, please choose another.")
            self.serialComm = None
            self.serial_initialized = False

    def readCustomBaudrateValue(self):
        self.baudrate = self.window.Element("baudrateCustomValue").Get()
        if ( self.baudrate == '' ):
            self.baudrate = None
        else:
            try:
                self.baudrate = int(self.baudrate)
            except Exception as e:
                self.baudrate = None
                print(e)


    def processWindowInput(self, event, values):
        if ( event == '__TIMEOUT__' ):
            None;

        elif ( event == "Exit" or event == None ):
            return -1;

        elif ( "baudrate" in event):
            if ( "Custom" not in event):
                self.baudrate = int(self.window.Element(event).Text)
            else:
                self.readCustomBaudrateValue();
            self.try_open_port()

        elif ( "port" in event ):
            try:
                self.port = self.window.Element(event+"Text").DisplayText
                if ( "None" in self.port ):
                    self.port = None
                else:
                    self.port = self.port[:self.port.find(" - ")]
            except Exception as e:
                print(e)

            if ( self.window.Element("baudrateCustom").Get() ):
                self.readCustomBaudrateValue();

            self.try_open_port();

        else:
            print(event)

        return 0;
