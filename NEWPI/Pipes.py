#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""主要是实现数据处理的‘管道’"""

from PyQt5 import QtCore
from  PyQt5.QtCore import QObject
from itertools import cycle
import  numpy as np
from numpy import  sin,pi
from collections import deque
angle=pi/180
import os
from  copy import deepcopy


def ReverseCode_lostone(lists):
    """实现补码,用于SPI数据后1位的情况"""
    lis=[0,0]
    lis[0]=lists[0]
    lis[1]=lists[1]
    temp = lis[0] & 0x40
    a = (lis[0] & 0x3f)
    if temp == 0x40:
        a = ~a & 0x3f
        b = (~(lis[1])) & 0xff
        return -(a*512+b*2+1)
    else:
        return a*512+lis[1]*2

def SetRange(value,(before_low,before_high),(after_low,after_high)):
    """将输入的value 控制在low-high之间"""
    return  (after_high-after_low)*value/(before_high-before_low)


#-----------以下为各种查找表-----------开始---------------

class SinDict_ForTest(object):
    """测试时候用的字典，无限产生sin的数值"""
    def __init__(self):
        self.value=cycle([sin(x*angle) for x in range(360)])
    def __getitem__(self, index):
        return self.value.next()
    def get(self,index,value):
        return self.value.next()

#实际用的一种编译补码的字典，没有调节范围
def LookupDict():
    LookupDict_0 = dict([(x, ReverseCode_lostone(x)) for x in [(m, n) for m in range(256) for n in range(256)]])
    return LookupDict_0
#有调节范围的字典
def LookupDict_SetRange(value,(before_low,before_high),(after_low,after_high)):
    temp=dict([(x, SetRange((ReverseCode_lostone(x)),(before_low,before_high),(after_low,after_high))) for x in [(m, n) for m in range(256) for n in range(256)]])
    return  temp


#-----------各种查找表-----------结束------------------------



#--------------------------------------
def Export(f_p):
    pass

def Pipe_Soft(N,np_arrary,section,unit_tosoft):
    """

    :param np_arrary: 数组
    :param section:
    :param unit_tosoft:
    :return:
    """
    weight = np.ones(N) / N

    pass

#-----------------数据处理部分---------------------------
class Barn(QObject):
    Signal_Unit_full=QtCore.pyqtSignal(int)
    def __init__(self,capacity,howmany=2,parent=None):
        super(Barn, self).__init__(parent)
        self._currentLocation=0
        self._capacity=capacity
        self._index=[True for i  in range(howmany) ]
        self._barns=dict([(i,deque(maxlen=capacity)) for i in [x for x in range(howmany)]])
        self.canBeUsed=0
        self.Signal_Unit_full.connect(self.choose)

    def saveIn(self,data):#自动选择存储的地方
        if self.canBeUsed!=-1:
            self._barns[self.canBeUsed].append(data)
            self._currentLocation+=1
            if self._currentLocation==self._capacity:
                self.Signal_Unit_full.emit(self.canBeUsed)
                self.canBeUsed=-1
                self._currentLocation=0

    def choose(self,fullindex):#挑选一个新的仓库,将fullindex仓库单元锁定
        self._index[fullindex]=False
        for index, data in enumerate(self._index):
            if data!=False:
                self.canBeUsed=data
                break
        else:
            self.canBeUsed=-1

    def upDataIndex(self,index,value=True):#更新可用仓库
        self._index[index]=value

    def lookBarnUnit(self,index):#锁定某个仓库单元
        self.choose(index)

    def __getitem__(self, item):
        return self._barns[item]



class Pipe(QObject):
    # Signal_inPipe=QtCore.pyqtSignal(str,tuple)
    # Signal_outPipe=QtCore.pyqtSignal(str,tuple)
    Signal_outPipe_ForWindow=QtCore.pyqtSignal(tuple,tuple,tuple)
    Siganl_outPipe_ForWidget=QtCore.pyqtSignal(str,str)#与主界面控件通信的模块
    def __init__(self,UnitCapacity,NumUnit,parent=None):
        super(Pipe,self).__init__(parent)
        self._barn=Barn(UnitCapacity,NumUnit,parent)
        self._barnThread=QtCore.QThread()
        self._barn.moveToThread(self._barnThread)
        self._barn.Signal_Unit_full.connect(self.PipeWork)
        self._barnThread.start()

    def inPipe(self,data):#输进管道的数据
        self._barn.saveIn(data)

    def outPipe(self,data):#管道流出的数据
        pass

    def PipeWork(self,index):#管道中进行的处理
        # print "barn work0",self._barn._index
        N=10
        weight = np.ones(N) / N
        data=np.array(self._barn[index])

        tempPressure= tuple(data[:,0])
        tempDistance = tuple(np.convolve(weight, data[:,1], 'valid'))
        self.Signal_outPipe_ForWindow.emit((0,1),(tempPressure,tempDistance),('r','g'))
        self._barn.upDataIndex(index)  # 更新仓库
        maxvalue = round(max(tempDistance),5)
        self.Siganl_outPipe_ForWidget.emit('MaxValue',str(maxvalue))

        # print "barn work1",self._barn._index


def isnum(text):
    """判断是不是数字"""
    for i in text:
        if i in '-.0123456789':
            pass
        else:
            return  False
    return True


class AllPara(QObject):
    data=dict()
    def equals(self,value):
        assert  isinstance(value,dict)
        self.data=deepcopy(value)

    def get(self,key):
        return  self.data[key]





if __name__=="__main__":
    pass



