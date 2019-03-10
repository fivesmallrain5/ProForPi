#!/usr/bin/env python
# -*- coding: utf-8 -*-

from  PyQt5 import QtCore
from copy import deepcopy

class QTimerTable(QtCore.QTimer):
    """
    时间表，通过addEvent(时间点，函数，次数）默认次数=-1表示每个循环都执行
    使用方式
    Timertable=QTimerTable(parent)
    Timertable.addEvent(5,function,-1)
    Timertable.timeout.connect(Timertable.xecuteTable)
    Timertable.start(unit_time)
    """
    def __init__(self, parent=None):
        super(QTimerTable, self).__init__(parent)
        self.TimeTable = {-1:[{self.Nonefun.__name__:[self.Nonefun,-1]},0]}
        self.endLoop = 0
        self.currentTime = 0
    def Nonefun(self):
        pass
    def setLoop(self,howlong):
        """设置一个时间循环的长度，是addTimeEvent中的when和howlong的最大值"""
        self.endLoop=howlong

    def addTimeEvent(self, when, functor, times=-1):
        """

        :param when: int 类型的时间点
        :param functor: 函数
        :param times: 执行的次数
        :return:
        """
        assert isinstance(when, int)
        if self.TimeTable.has_key(when):
            self.endLoop = max((max(self.TimeTable.keys()),self.endLoop))
            self.TimeTable.get(when)[0].setdefault(functor.__name__, [functor, times])
        else:
            self.endLoop = max((max(self.TimeTable.keys()),self.endLoop))
            self.TimeTable.setdefault(when, [{ functor.__name__ :[functor,times] },deepcopy(when)])


    def executeTable(self):
        self.currentTime += 1
        if self.currentTime > self.endLoop:
            self.currentTime = 0
        else:
            if self.currentTime in self.TimeTable.keys():
                for functorname in self.TimeTable.get(self.currentTime)[0].keys():
                    if self.TimeTable.get(self.currentTime)[0][functorname][1] > 0:
                        self.TimeTable.get(self.currentTime)[0][functorname][1] -= 1
                        self.TimeTable.get(self.currentTime)[0][functorname][0]()
                    elif self.TimeTable.get(self.currentTime)[0][functorname][1] == 0:
                        del self.TimeTable[self.currentTime][0][functorname]
                    else:
                        self.TimeTable.get(self.currentTime)[0][functorname][0]()



class MultipleQTimer(QTimerTable):
    """
    一个粗糙的计时器，可以有很多个，使用方式同QTimerTable，只不过addEvent()意思变了

    Timertable=QTimerTable(parent)
    Timertable.addEvent(5,function,-1):  参数：周期，函数，-1表示一直执行，其他数字表示执行的次数
    Timertable.timeout.connect(Timertable.xecuteTable)
    Timertable.start(unit_time)

    """
    def __init__(self, parent=None):
        super(MultipleQTimer, self).__init__(parent)

    def executeTable(self):
        for keytime in self.TimeTable.keys():
            if self.TimeTable[keytime][1] ==keytime:
                for functorname in self.TimeTable[keytime][0].keys():
                    # print functorname
                    self.TimeTable[keytime][0][functorname][0]()
                    self.TimeTable[keytime][1]-=1
                    if self.TimeTable[keytime][0][functorname][1] > 0:
                        self.TimeTable[keytime][0][functorname][1] -= 1
                    elif self.TimeTable[keytime][0][functorname][1] == 0:
                        del self.TimeTable[keytime][0][functorname]
                        if len(self.TimeTable[keytime][0])==0:
                            del self.TimeTable[keytime]
            elif self.TimeTable[keytime][1]==0:
                self.TimeTable[keytime][1]=deepcopy(keytime)
            else:
                self.TimeTable[keytime][1] -= 1







