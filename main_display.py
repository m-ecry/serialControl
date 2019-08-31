#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 15:18:24 2019

@author: omr-w
"""

import PySimpleGUI as sg

class mainDisplay(object):
    ndx = 0
    delta = 0
    moveThreshold  = 2
    right_border   = 0
    right_drawed_border = 0
    canvasAutoMove = 1
    range = 496;

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.right_border = self.width
        self.bordersize = 4
        self.graph = sg.Graph((640,512), (-self.bordersize,-self.bordersize), (self.width+self.bordersize,self.height+self.bordersize), background_color=None, key='display')

    def drawGrid(self):
        startX = self.right_drawed_border
        widthTimesX = 2
        if ( 0 == startX ):
            self.graph.DrawText("0", (-1.5,-1.5));

        self.right_drawed_border += widthTimesX*self.width

        self.graph.DrawLine((startX-self.delta,0), (self.right_drawed_border-self.delta,0), color='grey', width='3');

        widthStep = int(self.width/10)
        heightStep = int(self.height/10)
        for i in range(startX+widthStep,self.right_drawed_border+1, widthStep):
            self.graph.DrawLine((i-self.delta,0), (i-self.delta,self.height), color='grey', width='1');
            self.graph.DrawText(str(i)+'s', (i-self.delta,-1.5));
        for i in range(heightStep,self.height+1, heightStep):
            self.graph.DrawLine((startX-self.delta,i), (self.right_drawed_border-self.delta,i), color='grey', width='1');
            for j in range(widthTimesX+1):
                self.graph.DrawLine((startX-self.delta+j*self.width,0), (startX-self.delta+j*self.width,self.height), color='grey', width='3');
                self.graph.DrawText(str(i), (startX-self.delta-2+j*self.width,i-1.5));
                if ( 100 == i ):
                    self.graph.DrawText("T / °C", (startX-self.delta+5+j*self.width,i-1.5));


    def drawFullCanvas(self, graph):
        graph.Erase()
        self.drawGrid()
        #self.graph.Move((self.timeX[self.ndx] - self.timeX[self.ndx+1]), 0)
        for i in range(self.ndx):
            #graph.DrawLine( (self.timeX[self.ndx-i]-self.timeX[self.ndx-self.range], self.sensValue[self.ndx-i]*2+15),
                            #(self.timeX[self.ndx+1-i]-self.timeX[self.ndx-self.range], self.sensValue[self.ndx+1-i]*2+15),
            graph.DrawLine( (self.timeX[i], self.sensValue[i]*2+15),
                            (self.timeX[i+1], self.sensValue[i+1]*2+15),
                             color='blue', width=2)

    def fitCanvas(self, new_x_value):
        distanceToBorder = int((new_x_value+1) - self.right_border)
        #if new value is beyond the border, move border
        if ( (distanceToBorder > 0 ) and self.canvasAutoMove ):
            self.delta += distanceToBorder
            self.graph.Move(-distanceToBorder, 0)
            self.right_border += distanceToBorder

        # if Grid is drawn only one display length, draw it further
        if ( (self.right_drawed_border - self.width) < new_x_value ):
            self.drawGrid();

    def mvCanvas(self, left_direction):
        threshold = 20
        if ( left_direction ):
            if ( 0 <= (self.delta-threshold) ):
                self.delta -= threshold
                self.graph.Move(threshold, 0)
                self.right_border -= threshold
        else:
            if ( self.right_drawed_border >= (self.right_border + threshold) ):
                self.delta += threshold
                self.graph.Move(-threshold, 0)
                self.right_border += threshold

        # If moved outside of the graph, deactivate automovement
        if ( self.right_border < self.timeX[-1] ):
            self.canvasAutoMove = 0;
        else:
            self.canvasAutoMove = 1;
