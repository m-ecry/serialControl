#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 15:18:24 2019

@author: omr-w
"""

import PySimpleGUI as sg
from os import sys
import time

class mainDisplay(object):
    delta = 0
    moveThreshold  = 2
    right_border   = 0
    right_drawed_border = 0
    canvasAutoMove = 1
    range = 496;
    dataStreams = dict()
    markers = dict()

    def __init__(self, width, height, timePtr, timespan=100, background_color=None):
        """
        timespan: displayed timewindow
        xMin, xMax = xScale
        """
        self.gridConfig = {'xStepCnt':0, 'yStepCnt':0}
        self.bordersize = 40
        self.displayFieldSize = 1000
        self.right_border = timespan
        self.displaySize = (self.displayFieldSize + self.bordersize, self.displayFieldSize + self.bordersize)
        #self.labelGraphLeft = sg.Graph((width/20,height), (0,-self.bordersize), (self.displaySize[0]/20,self.displaySize[1]), background_color, key='labelDisplayLeft')
        self.graph = sg.Graph((width,height), (-self.bordersize,-self.bordersize), self.displaySize, background_color, key='mDisplay1')
        self.timeScale = self.displayFieldSize / timespan
        self.timePtr = timePtr

    def AddDataStream(self, timeDataPtr, yDataPtr, yScale, key, label=None):
        if ( key in self.dataStreams ):
            print("addDataStream: Key ", key, "already exists. Failed to create the datastream");
            return

        yMin, yMax = yScale
        if ( yMax < yMin ):
            tmp = yMax
            yMax = yMin
            yMin = tmp
        valueScale = self.displayFieldSize / (yMax-yMin)
        self.dataStreams[key] = { 'timeDataPtr':timeDataPtr,
                                  'valuePtr':   yDataPtr,
                                  'valueScale': valueScale,
                                  'yMin':       yMin,
                                  'yMax':       yMax,
                                  'Visible':    True,
                                  'lineIDs':    [],
                                  'lastDrawnIndex':0,
                                                                            }

        self.DrawGrid()
        self.UpdateGridLabel(yMin, yMax, valueScale, label=label)

    def UpdateGridLabel(self, yMin, yMax, valueScale, label=None):
        for j in range(self.gridConfig['forwardRender']):
            if ( label != None ):
                self.graph.DrawText(label,
                    (self.right_drawed_border-self.delta+7*len(label)+self.displayFieldSize*(j-2),yMax/valueScale-20));

            for i in range(self.gridConfig['yStepCnt']+1):
                valueLabel = i * self.gridConfig['heightStep'] / valueScale
                # 0 should not be displayed here, as it already was at the start
                if ( 0.01 > valueLabel ):
                    continue

                if ( (valueLabel % 10) > 0.01 ):
                    self.graph.DrawText("{:.2f}".format(valueLabel),
                        (self.right_drawed_border-self.delta-20+self.displayFieldSize*(j-2),i*self.gridConfig['heightStep']+20));
                else:
                    self.graph.DrawText("{:d}".format(int(valueLabel)),
                        (self.right_drawed_border-self.delta-20+self.displayFieldSize*(j-2),i*self.gridConfig['heightStep']+20));

    def DrawGrid(self, xStepCnt=10, yStepCnt=10):
        self.gridConfig['xStepCnt'] = xStepCnt
        self.gridConfig['yStepCnt'] = yStepCnt
        #How far the grid is drawn in advance (in displaylengths)
        self.gridConfig['forwardRender'] = 1 + 1;

        startX = self.right_drawed_border
        if ( 0 == startX ):
            self.graph.DrawText("0", (-20,-20));

        self.right_drawed_border += self.gridConfig['forwardRender']*self.displayFieldSize

        self.gridConfig['widthStep']  = int(self.displayFieldSize/xStepCnt)
        self.gridConfig['heightStep'] = int(self.displayFieldSize/yStepCnt)

        self.DrawLine((startX-self.delta,0), (self.right_drawed_border-self.delta,0), color='grey', width='3');

        for i in range(startX+self.gridConfig['widthStep'],self.right_drawed_border+1, self.gridConfig['widthStep']):
            self.DrawLine((i-self.delta,0), (i-self.delta,self.displayFieldSize), color='grey', width='1');
            timeLabel = i/self.timeScale
            if ( (timeLabel % 10) > 0.001 ):
                self.graph.DrawText("{:.2f}s".format(timeLabel), (i-self.delta,-20));
            else:
                self.graph.DrawText("{:d}s".format(int(timeLabel)), (i-self.delta,-20));

        for i in range(yStepCnt):
            currentPosition = (i+1) * self.gridConfig['heightStep']
            self.DrawLine((startX-self.delta,currentPosition), (self.right_drawed_border-self.delta,currentPosition), color='grey', width='1');
            for j in range(self.gridConfig['forwardRender']+1):
                self.DrawLine((startX-self.delta+j*self.displayFieldSize,0), (startX-self.delta+j*self.displayFieldSize,self.displayFieldSize), color='grey', width='3');

    def drawFullCanvas(self, graph):
        self.graph.Erase()
        self.drawGrid()
        #self.graph.Move((self.timeX[self.ndx] - self.timeX[self.ndx+1]), 0)
        for i in range(self.ndx):
            #graph.DrawLine( (self.timeX[self.ndx-i]-self.timeX[self.ndx-self.range], self.sensValue[self.ndx-i]*2+15),
                            #(self.timeX[self.ndx+1-i]-self.timeX[self.ndx-self.range], self.sensValue[self.ndx+1-i]*2+15),
            self.graph.DrawLine( (self.timeX[i], self.sensValue[i]*2+15),
                            (self.timeX[i+1], self.sensValue[i+1]*2+15),
                             color='blue', width=2)

    def HideDataset(self, key=None):
        if ( key == None ):
            print("HideDataLine needs a key, abort")
        elif ( key not in self.dataStreams ):
            print("No such dataStream")
        else:
            self.DeleteDataset(key)
            self.dataStreams[key]['Visible'] = False

    def RestoreLine(self, dataX, dataY, key=None):
        if key is None:
            print("RestoreLine: No key was given.")
            return;
        elif key not in self.dataStreams:
            print("RestoreLine: key doesnt belong to dataStream.")
            return;
        stream = self.dataStreams[key]
        stream['Visible'] = True
        for i in range(len(stream['valuePtr'])-2):
            self.DrawLine2( (stream['timeDataPtr'][i]-self.delta, stream['valuePtr'][i]), (stream['timeDataPtr'][i+1]-self.delta, stream['valuePtr'][i+1]), color='blue', width=2, key='temperature')

    def DeleteDataset(self, key=None):
        if key is None:
            print("DeleteLine: No key was given.")
            return;
        elif key not in self.dataStreams:
            print("DeleteLine: key doesnt belong to dataStream.")
            return;

        #print(len(self.dataStreams[key]['valuePtr']))
        #print(self.dataStreams[key]['lineIDs'])
        for id in self.dataStreams[key]['lineIDs']:
            self.graph.DeleteFigure(id)
        self.dataStreams[key]['lineIDs'] = []

    def DrawLine(self, pointFrom, pointTo, color='black', width=1, key=None):
        #if key not in self.ids:
            #self.ids[key] = []

        if ( key is not None and key not in self.hiddenIDs ):
            self.ids[key].append(self.graph.DrawLine(pointFrom, pointTo, color, width))
        else:
            self.graph.DrawLine(pointFrom, pointTo, color, width)

    def DrawLine2(self, pointFrom, pointTo, color='black', width=1, key=None):
        if key not in self.dataStreams:
            print("DrawLine2: Before adding data to a stream, first add one")
            return;

        pointFrom = (pointFrom[0]*self.timeScale, pointFrom[1]*self.dataStreams[key]['valueScale'])
        pointTo   = (pointTo[0]*self.timeScale,   pointTo[1]*self.dataStreams[key]['valueScale'])
        if ( self.dataStreams[key]['Visible'] ):
            self.dataStreams[key]['lineIDs'].append(self.graph.DrawLine(pointFrom, pointTo, color, width))
        #else:
            #self.graph.DrawLine(pointFrom, pointTo, color, width)

    def DrawLevelMarker(self, level, key=None, color='black', width=1):
        if ( key == None ):
            print("DrawLevelMarker: missing key");
            return -1
        elif ( key not in self.dataStreams ):
            print("DrawLevelMarker: Key does not belong to a datastream")
            return -1

        level *= self.dataStreams[key]['valueScale']
        if ( 'marker' in self.dataStreams[key] ):
            #Only do something, when the marker is different
            if ( self.dataStreams[key]['marker']['value'] == level ):
                return 0;
            self.graph.DeleteFigure(self.dataStreams[key]['marker']['id'])
        else:
            self.dataStreams[key]['marker'] = dict()

        self.dataStreams[key]['marker']['value'] = level
        self.dataStreams[key]['marker']['id'] = self.graph.DrawLine(
            (-self.delta,level), (self.right_drawed_border, level), color, width )

    def updateGraph(self):
        #print('update')
        for key in self.dataStreams:
            stream = self.dataStreams[key]
            #first new elemetn
            if ( stream['Visible'] ):
                while ( stream['lastDrawnIndex'] < (len(stream['valuePtr'])-1) ):
                    #print(stream['lastDrawnIndex'])
                    self.DrawLine2( (stream['timeDataPtr'][stream['lastDrawnIndex']]-self.delta, stream['valuePtr'][stream['lastDrawnIndex']]),
                                    (stream['timeDataPtr'][stream['lastDrawnIndex']+1]-self.delta, stream['valuePtr'][stream['lastDrawnIndex']+1]),
                                     color='blue', width=2, key=key)

                    stream['lastDrawnIndex'] += 1

        self.fitCanvas(self.timePtr[-1])

    def fitCanvas(self, new_x_value):
        distanceToBorder = int((new_x_value+1) - self.right_border)
        #print("fit:", new_x_value, distanceToBorder, self.right_border)
        #if new value is beyond the border, move border
        if ( (distanceToBorder > 0 ) and self.canvasAutoMove ):
            self.delta += distanceToBorder
            self.graph.Move(-distanceToBorder*self.timeScale, 0)
            self.right_border += distanceToBorder

        # if Grid is drawn only one display length in advance, draw it further
        if ( (self.right_drawed_border - self.displayFieldSize) < new_x_value*self.timeScale ):
            self.DrawGrid();

    def mvCanvas(self, direction):
        threshold = 5
        if ( 'left' == direction ):
            if ( 0 <= (self.delta-threshold) ):
                self.graph.Move(threshold*self.timeScale, 0)
                self.delta -= threshold
                self.right_border -= threshold*self.timeScale
            else:
                self.graph.Move(self.delta, 0)
                self.delta = 0
                self.right_border = self.displayFieldSize
        elif ( 'right' == direction ):
            if ( self.right_drawed_border >= (self.right_border + threshold*self.timeScale) ):
                self.graph.Move(-threshold*self.timeScale, 0)
                self.delta += threshold
                self.right_border += threshold*self.timeScale

        # If moved outside of the graph, deactivate automovement
        if ( self.right_border < self.timePtr[-1] ):
            self.canvasAutoMove = 0;
        else:
            self.canvasAutoMove = 1;
