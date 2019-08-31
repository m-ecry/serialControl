#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 15:18:24 2019

@author: omr-w
"""

import PySimpleGUI as sg
from serial_comm import serial_communication as sc
import serial_utils as sutils
import time
import signal
import shutil
import os
currentMS = int(round(time.time() * 1000))
from main_display import mainDisplay as md

class mainWindow(object):
    """ Main Window for the regulator """

    timeX = [0]
    sensValue = [0]

    def __init__(self, port, baudrate):
        self.filename = ".tmp.csv"
        self.serial_initialized = 0;
        if ( port != None and baudrate != None ):
            self.startSerial(port, baudrate)

        with open(self.filename, 'w') as outfile:
            outfile.write("Time in s since start, InputValue\n");


        self.refresh_serial_port_list();
        self.setup();

    def refresh_serial_port_list(self):
        self.ports = ['Refresh port list']
        self.ports += sutils.listAvailablePorts(1)

        self.menu_def = [ ['File', ['Change Output File To...', 'Exit',]],
                     ['Serial', self.ports ],
                     ['Help', 'About'], ]


    def setup(self):
        self.mDisplay = md(100,100)

        # heigth in rows, witdth in pixels
        size_progressBar = (50,32)
        padding = ((0,0),0)
        colpadding = ((0,0),8)

        col1 = [ [ sg.Button(button_text="<", size=(1,30), key='mv_left'),
                   self.mDisplay.graph,
                   sg.Button(button_text=">", size=(1,30), key='mv_right') ], ]

        col2 = [ [ sg.Text("Cur", size=(4,1), pad=padding), sg.Text(' 0.00', key='_sensor', size=(5,1), pad=padding), ],
                 [ sg.Text("Dest", size=(4,1), pad=padding), sg.Text('0.00', key='_output', size=(5,1), pad=padding) ],
                   ]

        col3 = [ [ sg.Text("Set", size=(5,1), justification='right'), ],
                 [ sg.Slider(range=(0,100), default_value=0, orientation='v', size=(24,20), key='temp', pad=padding), ], ]

        temperature_frame_layout = [ [ sg.Column(col2, pad=colpadding),
                                       sg.Column(col3, pad=colpadding),
                                                                            ], ]

        layout = [  [ sg.Menu(self.menu_def, key='menu') ],
                    [
                      sg.Column(col1, pad=colpadding),
                      sg.Frame("Temperature in °C", temperature_frame_layout), ], ]

        self.window = sg.Window('serial control', layout, auto_size_text=True, default_element_size=(40, 1))
        event, self.oldValues = self.window.Read(timeout=1)
        print(self.oldValues)

        self.mDisplay.drawGrid();
        self.startTime = int(round(time.time() * 1000));

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

    def run(self):
        while True:
            event, values  = self.window.Read(timeout=50)
            if ( 0 > self.processWindowInput(event, values) ):
                    break;

            if ( self.serial_initialized ):
                self.evaluateReceivedValues( self.serialComm.listenToPort() )

        if ( self.serial_initialized ):
            self.serialComm.closeComm();
        self.window.Close()

    def showWarning(self, title, warning):
        sg.PopupNoWait( warning,
                        title=title,
                        background_color='Yellow',
                        keep_on_top=True)

    def storeValues(self, x, y):
        with open(self.filename, 'a+') as outfile:
            #outstring = str(x) + ',' + str(y) + '\n'
            outstring = "{:.4f},{:.4f},\n".format(x, y)
            outfile.write(outstring)

    def storeDataToCustomFile(self, customFile):
        try:
            shutil.copy2(self.filename, customFile) # complete target filename given
            self.filename = customFile
        except Exception as e:
            self.showWarning("Error while opening file", str(e));

    def evaluateReceivedValues(self, values):
        if ( 0 != values ):
            #print(values);
            try:
                currentMS = int(round(time.time() * 1000))
                self.timeX.append(float((currentMS - self.startTime)/100))

                tmp = float(values['sensor'] * 100 / 4096.0); # 12-bit adc-values
                #print (tmp)
                self.sensValue.append( tmp )

                self.mDisplay.fitCanvas(self.timeX[-1])

                self.mDisplay.graph.DrawLine( (self.timeX[-2]-self.mDisplay.delta, self.sensValue[-2]),
                                     (self.timeX[-1]-self.mDisplay.delta, self.sensValue[-1]),
                                      color='blue', width=2)

                self.storeValues(self.timeX[-1], self.sensValue[-1])

                self.window.Element('_sensor').Update("%.2f"%tmp)
                values['output'] = int(values['output'])
                self.window.Element('_output').Update(values['output'])
                ########################################################################

                if ( not hasattr(self,'lastReceivedValues') ):
                    self.lastReceivedValues = values

                if ( self.lastReceivedValues['output'] != values['output'] ):
                    if ( hasattr(self, 'line') ):
                        self.graph.DeleteFigure(self.line)

                    self.line = self.graph.DrawLine( (0, values['output']),
                                         (self.right_drawed_border, values['output']),
                                         color='red', width=1)

                self.lastReceivedValues = values
                # In case, a change was missed, repeat report current value
                if ( self.oldValues['temp'] != int(values['output']) ):
                    self.serialComm.writeToPort(self.oldValues['temp']);

            except Exception as e:
                print("Value", e, "could not be found")
                print("Complete value list:", values)

    def check_if_value_changed(self, values):
        # If value has changed, do action
        currentKey = 'temp'
        if ( self.oldValues[currentKey] != values[currentKey] ):
            try:
                values['temp'] = int(values['temp'])
                if ( 100 < values['temp'] ):
                    raise Exception("Temperature must be between 0 and 100°C.");

                self.serialComm.writeToPort(values['temp']);
                time.sleep(0.01);
            except Exception as e:
                self.showWarning('Invalid temperature given!', str(e));

        self.oldValues = values

    def processWindowInput(self, event, values):
        if ( event == '__TIMEOUT__' ):
            self.check_if_value_changed(values)
            return 0;
        #else:
            #print(event)

        if ( event is None or event == 'Exit' ):
            return -1;
        elif ( event == 'temp' ):
            values['temp'] = int(values['temp'])
            if ( self.oldValues['temp'] != values['temp'] ):
                try:
                    values['temp'] = int(values['temp'])
                    if ( 100 < values['temp'] ):
                        raise Exception("Temperature must be between 0 and 100°C.");

                    self.serialComm.writeToPort(values['temp']);
                    time.sleep(0.1);
                except Exception as e:
                    self.showWarning('Invalid temperature given!', str(e));

        elif ( event == 'mv_right' ):
            self.mDisplay.mvCanvas(0);
        elif ( event == 'mv_left' ):
            self.mDisplay.mvCanvas(1);
        elif ( event == 'Change Output File To...'):
            newFile = sg.PopupGetFile("Choose file to store the data into.", title='New savefile', save_as=True, file_types=(('csv file', '*.csv'),), no_window=True)
            if ( newFile != None ):
                print('store now into ', newFile)
                self.storeDataToCustomFile(newFile);
        elif ( event == 'About' ):
            about_text = "Created by omr-w, Dresden 2019 under MIT-Licence.\n\n\nIt should help evaluate sensor data, collected by a uC. It uses a simple serial protocoll and for arduino this serial protocol can be used with help of an library, to find on my github-profile.\n\nFeel free to visit me under https://github.com/omr-w"
            about_layout = [ [ sg.Text(about_text, size=(40,14), key='_about') ] ]

            window = sg.Window("About", about_layout, auto_size_text=True)
            window.Read(timeout=0)
        elif ( event in self.ports ):
            if ( event == self.ports[0] ):
                self.refresh_serial_port_list();
                self.window.Element('menu').Update(menu_definition=self.menu_def)
            else:
                for port in self.ports:
                    if ( event == port ):
                        print(port[:port.find(" - ")])
                        self.startSerial(event[:event.find(" - ")], 9600)

        self.oldValues = values

        return 0;

    def updateElement(self, name, value):
        self.window.Element(name).Update(value);
