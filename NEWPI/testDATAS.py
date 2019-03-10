#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets,QtCore
from numpy import  sin,pi
angle=pi/180
class DATA(QtCore.QObject):
    Signal_Data2Window=QtCore.pyqtSignal(tuple,tuple,tuple)#
    Signal_DataOneLine=QtCore.pyqtSignal(tuple,tuple,tuple)#
    Signal_Data2DataBase=QtCore.pyqtSignal(str,int,float,float)
    table=None

    index=0
    datax=0
    color=['r','g']
    datay=[sin(x*angle) for x in [i for i in range(360) ] ]
    workon=True

    def SlotSendData(self):
        if self.workon:
            if self.datax==359 :
                self.datax = 0
            self.Signal_Data2Window.emit((self.index,self.index),(self.datay[self.datax],self.datay[self.datax]+1),(0,1))
            self.Signal_DataOneLine.emit((0,),(self.datay,),(self.color[self.datax%2],))
            # print self.index,self.datay[self.datax]
            if self.table is not None:
                self.Signal_Data2DataBase.emit(self.table,int(self.index),float(self.datay[self.datax]),float(self.datay[self.datax]))
                # print'db'
            self.index += 1
            self.datax+=1

    def SlotTableGet(self,path,table):
        self.table=table

