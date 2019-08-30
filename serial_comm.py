# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 20:58:16 2019

@author: omr-w
"""

import serial

class serial_communication(object):
    """This class handles the serial communication to and from the uC-board """
    inBuffer = b''

    def __init__(self, port, baudrate):
        self.port = port;
        self.baudrate = baudrate;
        self.ser = serial.Serial( port=port,
                                  baudrate=baudrate,
                                  bytesize=8,
                                  parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE,
                                  #xonxoff=True,
                                  #rtscts=True,
                                  #dsrdtr=True,
                                  timeout=0                       );

        print("Serial was initialized on Port", self.port)

    def openComm(self):
        try:
            self.ser.open();
        except:
            print("Port already open")

    def closeComm(self):
        try:
            self.ser.close();
        except:
            print("Port already closed")

    def listenToPort(self):
        self.inBuffer += self.ser.read(30);

        if ( len(self.inBuffer) ):
            try:
                received = self.inBuffer.decode('ascii')
                #print(received)
                start = received.find('#');
                end   = received.find('\r\n');

                # If not both starting and ending byte can be found, return
                #   and wait for more data
                if ( (0 > start) or (0 > end) or (start > end) ):
                    # Throw away bad formatted data
                    self.inBuffer = self.inBuffer[start:]
                    return 0

                data = received[start:end]

                #Further dumping ill formatted data
                is_one_frame = data.rfind('#')
                while ( is_one_frame > 0):
                    data = data[is_one_frame:]
                    is_one_frame = data.rfind('#')

                # Cut the extracted data from the buffer
                self.inBuffer = self.inBuffer[end+2:]

                # Extracting given datalength, adding framesize
                length = int(data[1:3]) + 4
                # if datalength is according to send length + framesize
                if ( (end-start) == length ):
                    return self.evaluateSerialCommunication(data)
            except Exception as e:
                print("serialRX error.\nbuffer: ", self.inBuffer)
                if ( 'data' in locals() ):
                    print("data: ", data)
                else:
                    print("data: ", "No complete data frame collected yet")
                print(e, '\n')
                #clear buffer:
                self.inBuffer = b''
                return 0

        return 0;

    def writeToPort(self, input):
        checksum = 60; #offset for char conversion of checksum above '#' and ';'
        tmp = input

        while ( tmp > 0 ):
            checksum += (tmp % 10);
            tmp = int(tmp / 10);

        outstring = str(input);
        outstring = '#' + str(len(outstring)) + outstring + chr(checksum) + ';';
        outbytes = outstring.encode('ascii');
        #print(outbytes)
        self.ser.write(outbytes);

    def evaluateSerialCommunication(self, comm):
        if ( comm[0] != '#' ):
                return 0;

        elements = comm[1:].split(';')
        # Pop last element, which is empty
        elements.pop()
        length = int(elements.pop(0));

        values = [ e.split('=') for e in elements ]
        response = dict( (name, int(value)) for name, value in values )

        return response

    def clearBuffer(self):
        self.ser.reset_output_buffer();
        self.ser.reset_input_buffer();
