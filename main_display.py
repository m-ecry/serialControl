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

    def __init__(self, width, height, timePtr, timeSpan=100, background_color=None):
        """
        timespan: displayed timewindow
        xMin, xMax = xScale
        """
        self.gridConfig = {'xStepCnt':0, 'yStepCnt':0}
        self.bordersize = 5
        self.xLimit  = 100
        self.yLimit = 100
        labelFraction = 10
        self.labelWindowWidth = 10#self.xLimit/labelFraction
        self.right_border = timeSpan
        self.timeScale = self.xLimit / timeSpan
        self.labelGraphLeft = sg.Graph((width/labelFraction,height), (self.labelWindowWidth,-self.bordersize), (0,self.yLimit+self.bordersize), background_color, pad=(0,0), key='labelDisplayLeft')
        self.labelGraphRight= sg.Graph((width/labelFraction,height), (0,-self.bordersize), (self.labelWindowWidth,self.yLimit+self.bordersize), background_color, pad=(0,0), key='labelDisplayRight')
        self.graph = sg.Graph((width,height), (-2,-self.bordersize), (self.xLimit+2, self.yLimit+self.bordersize), background_color, pad=(0,0), key='mDisplay1')
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
        valueScale = self.yLimit / (yMax-yMin)
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
        if ( label != None ):
            self.labelGraphLeft.DrawText(label,(6,yMax/valueScale-5), angle=90);

        self.labelGraphLeft.DrawLine((0,0), (0,self.yLimit), color='grey', width=3)

        for i in range(self.gridConfig['yStepCnt']+1):
            valueLabel = i * self.gridConfig['yStepSize'] / valueScale
            self.labelGraphLeft.DrawLine((1.5,i*self.gridConfig['yStepSize']), (0,i*self.gridConfig['yStepSize']), color='grey', width=1)

            if ( (valueLabel % 10) > 0.01 ):
                self.labelGraphLeft.DrawText("{:.2f}".format(valueLabel),
                    (2,i*self.gridConfig['yStepSize']+2));
            else:
                self.labelGraphLeft.DrawText("{:d}".format(int(valueLabel)),
                    (2,i*self.gridConfig['yStepSize']+2));

    def DrawGrid(self, xStepCnt=10, yStepCnt=10):
        self.gridConfig['xStepCnt'] = xStepCnt
        self.gridConfig['yStepCnt'] = yStepCnt
        #How far the grid is drawn in advance (in displaylengths)
        self.gridConfig['forwardRender'] = 1 + 1;

        startX = self.right_drawed_border

        self.right_drawed_border += self.gridConfig['forwardRender']*self.xLimit

        self.gridConfig['xStepSize']  = int(self.xLimit/xStepCnt)
        self.gridConfig['yStepSize'] = int(self.yLimit/yStepCnt)

        self.DrawLine((startX-self.delta,0), (self.right_drawed_border-self.delta,0), color='grey', width='3');

        for i in range(startX,self.right_drawed_border+1, self.gridConfig['xStepSize']):
            self.DrawLine((i-self.delta,0), (i-self.delta,self.yLimit), color='grey', width='1');
            timeLabel = i/self.timeScale
            if ( (timeLabel % 10) > 0.001 ):
                self.graph.DrawText("{:.2f}s".format(timeLabel), (i-self.delta,-2));
            else:
                self.graph.DrawText("{:d}s".format(int(timeLabel)), (i-self.delta,-2));

        for i in range(yStepCnt):
            currentPosition = (i+1) * self.gridConfig['yStepSize']
            self.DrawLine((startX-self.delta,currentPosition), (self.right_drawed_border-self.delta,currentPosition), color='grey', width='1');

        self.RefreshLevelMarker()

    def drawFullCanvas(self, graph):
        self.graph.Erase()
        self.drawGrid()
        #self.graph.Move((self.timeX[self.ndx] - self.timeX[self.ndx+1]), 0)
        for i in range(self.ndx):
            #graph.DrawLine( (self.timeX[self.ndx-i]-self.timeX[self.ndx-self.range], self.sensValue[self.ndx-i]*2+15),
                            #(self.timeX[self.ndx+1-i]-self.timeX[self.ndx-self.range], self.sensValue[self.ndx+1-i]*2+15),
            self.graph.DrawLine( (self.timeX[i], self.sensValue[i]*2+2),
                            (self.timeX[i+1], self.sensValue[i+1]*2+2),
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

    def RefreshLevelMarker(self):
        for key in self.dataStreams:
            if 'marker' in self.dataStreams[key]:
                self.graph.DeleteFigure(self.dataStreams[key]['marker']['id'])
                self.dataStreams[key]['marker']['id'] = None

                self.dataStreams[key]['marker']['id'] = self.graph.DrawLine(
                    (-self.delta, self.dataStreams[key]['marker']['value']),
                    (self.right_drawed_border, self.dataStreams[key]['marker']['value']),
                    self.dataStreams[key]['marker']['color'],
                    self.dataStreams[key]['marker']['width'] )

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
            self.dataStreams[key]['marker']['id'] = None
        else:
            self.dataStreams[key]['marker'] = dict()

        self.dataStreams[key]['marker']['value'] = level
        self.dataStreams[key]['marker']['color'] = color
        self.dataStreams[key]['marker']['width'] = width
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
                    self.DrawLine2( (stream['timeDataPtr'][stream['lastDrawnIndex']]*self.timeScale-self.delta, stream['valuePtr'][stream['lastDrawnIndex']]),
                                    (stream['timeDataPtr'][stream['lastDrawnIndex']+1]*self.timeScale-self.delta, stream['valuePtr'][stream['lastDrawnIndex']+1]),
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
        if ( (self.right_drawed_border - self.xLimit) < new_x_value*self.timeScale ):
            self.DrawGrid();

    def mvCanvas(self, direction):
        threshold = 5
        if ( 'left' == direction ):
            if ( 0 <= (self.delta-threshold) ):
                self.graph.Move(threshold*self.timeScale, 0)
                self.delta -= threshold
                self.right_border -= threshold
            else:
                self.graph.Move(self.delta, 0)
                self.delta = 0
                self.right_border = self.xLimit
        elif ( 'right' == direction ):
            if ( self.right_drawed_border >= (self.right_border + threshold)*self.timeScale ):
                self.graph.Move(-threshold*self.timeScale, 0)
                self.delta += threshold
                self.right_border += threshold

        # If moved outside of the graph, deactivate automovement
        if ( self.right_border < self.timePtr[-1] ):
            self.canvasAutoMove = 0;
        else:
            self.canvasAutoMove = 1;
