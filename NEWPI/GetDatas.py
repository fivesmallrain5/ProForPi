#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""获取数据"""

from PyQt5 import QtWidgets,QtCore,QtGui
from  PyQt5.QtCore import QObject
from Pipes import  ReverseCode_lostone,SinDict_ForTest,LookupDict_SetRange
from ADS1120IPWR import  ADS1120 as ad
import random
class GetDataObj(QObject):
    #各种信号
    Siganl_ManagerWidget_ForGetData=QtCore.pyqtSignal(str,str)#用于操作主界面的
    # 给数据控制模块，希望存储的数据
    Signal_ForSaving=QtCore.pyqtSignal(str,int,float,float)#表名，时间ID，压力，位移
    # 给界面绘曲线用的（逐点的方式）
    # Signal_Data2Window = QtCore.pyqtSignal(tuple, tuple, tuple)  # (x1，x2，..),（y1,y2...）,(曲线1标号，曲线2标号）
    Signal_Data2Window = QtCore.pyqtSignal(tuple, tuple)#（y1,y2...）,(曲线1标号，曲线2标号）
    Signal_ForPipes=QtCore.pyqtSignal(tuple)#给数据处理部分的数据
    Siganl_GetDatasError=QtCore.pyqtSignal(str,str)#错误信息绑定
    #各种变量
    whichway=False
    table = None
    WorkON=True
    Pause_1=True
    Pause_2=True
    currentWorkType='None'#进行的工作种类，'Power':电压查询，
    timeId=0
    WorkLine=['None',]#工作队列，工作前提WorkON=True，Pause_F=False
                    #,WorkLine[0]是永运会被执行，但它被执行是在工作队列
                    # 中只剩它一个的时候，WorkLine[1...]之后添加的工作会被执行一次，
                    #然后移除工作队列，其执行次序优于WorkLine[0],在设置其他工作的时候一定
                    #让各种工作的时间的周期尽量不一样，否则容易workline一次添加多个同时工作
                    #但只能在同一时刻处理一种工作，最后工作队列满了。


    def __init__(self):
        super(GetDataObj, self).__init__(None)
        #查找表的配置
        self.LookupTable = SinDict_ForTest()#更改查找表，就会更改数据接收的值
        self.myAD = ad(1, 0)  # ad 实体化，包含初始化的参数设置了
        #注册各种方法
        self.WorkTypeMethodDict={
            'None':self.NoneWork,
            'Power':self.GetPower,
            'Link':self.GetLink,
            'M_Data':self.GetData,
                           }
#-----------------------------操作性质的方法-----------------------------

    def Working(self):
        """调用其他方法的总执行的地方,与计时器绑定"""
        if self.WorkON:
            if not (self.Pause_1 and self.Pause_2):
                if len(self.WorkLine)>1:
                    self.currentWorkType=self.WorkLine.pop()
                    self.Pause_2=True
                else:
                    self.currentWorkType=self.WorkLine[0]
                self.WorkTypeMethodDict.get(self.currentWorkType,'None')()


    def SetPauseOrNot(self,value):
        """控制暂停的"""
        self.Pause_1=value


    def Close(self):
        """模块退出的"""
        self.WorkON=False
        print "数据获取退出"

    def SetWorkType(self,TheType,forever='True'):
        """设置当前工作的种类，forever=True表示会被永远执行"""
        if forever=='True':
            self.WorkLine[0] = TheType
        else:
            self.WorkLine.append(TheType)
            self.Pause_2=False




#-----------------特殊的方法,各种需要通过AD操作的方法就写在下面，
# ----------------然后在初始化函数中注册-------------------------------



    #------------------获取数据部分的一些方法--------------------
    def SetTableForSaving(self,path,table):
        """用于设置表"""
        self.table=table
    def SetWhichWays(self,ways):
        self.whichway=ways
        print "setwhichway", self.whichway

    def GetData(self):
        """获取数据,"""
        if self.table is not None:
            # print 'Datageting'
            self.timeId+=1
            tempPressure=self.LookupTable.get(self.myAD.GetAD(1),5)+random.random()
            # tempDistance=self.LookupTable.get(self.myAD.GetAD(2),6)
            tempDistance=tempPressure+2
            #存储数据的信号发送
            self.Signal_ForSaving.emit(self.table,int(self.timeId),float(tempPressure),float(tempDistance))
            if self.whichway :
                #绘图的数据
                self.Signal_Data2Window.emit((tempPressure,tempDistance),(0,1))
            else:
                self.Signal_ForPipes.emit((tempPressure,tempDistance))
#----------------------------------------------------------
    def GetPower(self):
        """获取电压"""

        print 'power woring'
        tempPower = self.LookupTable.get(self.myAD.GetAD(3), 5)
        #电压解析
        self.Siganl_ManagerWidget_ForGetData.emit('Power','1')

    def GetLink(self):
        """设备连接状态获取"""
        print 'link woring'
        if self.myAD.GetAD(3)!= (0,0):
            self.Siganl_ManagerWidget_ForGetData.emit('Link','True')
        else:
            self.Siganl_ManagerWidget_ForGetData.emit('Link','False')



    def NoneWork(self):
        pass
