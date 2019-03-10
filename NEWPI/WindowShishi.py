#!/usr/bin/env python
# -*- coding: utf-8 -*-
#实时显示窗口类
import  numpy as np
from  PyQt5.QtCore import QObject
from  PyQt5 import  QtCore
import  pyqtgraph as pg
from Pipes import Barn
from collections import  deque
"""
1.两种增加数据的方式，通过信号槽来传递数据的话，逐点传送数据快，线传递数据慢
    所以如果实时绘图的话，用第一种，数据缓慢变化，可以用第二种方式
2.颜色选择：字符形式允许： r, g, b, c, m, y, k, w


"""

class ShowWindow(QObject):
    Signal_showwindowForWidget=QtCore.pyqtSignal(str,str)#与主界面控件通信用的
    def __init__(self, UIpoint, parent=None):
        super(ShowWindow, self).__init__(parent)
        pg.setConfigOption('background', 'k')
        pg.setConfigOption('foreground', 'd')
        pg.setConfigOptions(antialias=True)
        self.Allpara = dict()  # 保存参数表里面的参数，这个才是真正的用于各种计算的参数
        # 其他模块也有这个参数ALLpara,这个模块的参数一旦变换，所有模块的这个参数都会变化
        self.UIpoint = UIpoint  # 界面指针
        self.UIpoint.clear()
        self.viewbox = CustomViewBox()
        self.myplot = pg.PlotItem(viewBox=self.viewbox)#画布设置
        self.myplot.showGrid(x=True, y=True)
        self.myplot.setLabel('left', "Pressure", units='MPa')
        self.UIpoint.addItem(self.myplot)
        self.MaxPoints=300
        self.x= 0
        self.curveitems=dict()#{曲线名：（曲线类，曲线数据x,曲线数据y）}
        self.workon=False
        N = 20
        self.weight = np.ones(N) / N
        self.wightbag=deque((0 for i in range(N)),maxlen=N)
        self.Maxvalue=0

        #----------------------------------新的尝试，将pipe安装在这里
        # self.curveitems3 = dict()
        # self.newbarn=Barn(self.MaxPoints,2,self)
        # self.newbarn.Signal_Unit_full.connect(self.PipeWork)
        # N = 10
        # self.weight = np.ones(N) / N
        # self.newbarn_x=[i for i in range(self.MaxPoints)]




#------方法1----------------当发送的数据为点时用下面的---------------------------
    #曲线会为实时动态的。
    def clearCurve(self):
        """清除所有曲线"""
        self.curveitems = dict()


    def setCurves(self,curvename=(0,),colors=('r',)):
        """增加曲线的个数"""
        for (name,color) in zip(curvename,colors):
            plocrveitem=pg.PlotCurveItem(pen=pg.mkPen(color))
            self.curveitems.setdefault(name,(plocrveitem,deque(maxlen=self.MaxPoints),deque(maxlen=self.MaxPoints)))
            self.myplot.addItem(self.curveitems.get(name)[0])
    def addPoints2curves(self,py=(0,),namelists=(0,)):
        """给每条曲线增加点"""
        if self.workon:
            self.myplot.clear()
            for index,name in enumerate(namelists):
                if len(self.curveitems.get(name)[1])<self.MaxPoints:
                    self.curveitems.get(name)[1].append(self.x)  # 增加x数据
                    self.x+=1
                self.curveitems.get(name)[2].append(py[index])#增加y数据
            for name in self.curveitems.keys():
                self.curveitems.get(name)[0].setData(x=np.array(self.curveitems.get(name)[1]),
                                                     y=np.array(self.curveitems.get(name)[2]))
                self.myplot.addItem(self.curveitems.get(name)[0])

    def addPoints2curvesFIlter(self, py=(0,), namelists=(0,)):
        """给每条曲线增加点"""
        if self.workon:
            self.myplot.clear()
            for index, name in enumerate(namelists):
                if len(self.curveitems.get(name)[1]) < self.MaxPoints:
                    self.curveitems.get(name)[1].append(self.x)  # 增加x数据
                    self.x += 1
                if index==0:#0是原始
                    self.curveitems.get(name)[2].append(py[index])  # 增加y数据
                else:#1是过滤后的
                    self.wightbag.append(py[index])
                    b = np.convolve(self.weight, self.wightbag, 'valid')
                    b=b[0]
                    self.curveitems.get(name)[2].append(b)
                    self.Maxvalue=b if  b>self.Maxvalue else self.Maxvalue#获取最大值
                    self.Signal_showwindowForWidget.emit('MaxValue',str(self.Maxvalue))




            for name in self.curveitems.keys():
                self.curveitems.get(name)[0].setData(x=np.array(self.curveitems.get(name)[1]),
                                                     y=np.array(self.curveitems.get(name)[2]))
                self.myplot.addItem(self.curveitems.get(name)[0])



#--------方法2--------当发送的数据为一条线数据时用这个-----------------------------------------
#直接显示一条曲线，不动态，
    def addLines(self,namelists=(0,),liney=((0,),),colors=('r',)):
        """直接增加一条曲线并显示"""
        if self.workon:
            self.myplot.clear()
            for index,name in enumerate(namelists):
                lineydata = np.array(liney[index])
                self.myplot.plot(lineydata,pen=pg.mkPen(colors[index]))

# --------方法3---------------------------------------
    #每self.maxpoints处理一次数据
    # def setCurves3(self,curvename=(0,),colors=('r',)):
    #     """增加曲线的个数"""
    #     for (name,color) in zip(curvename,colors):
    #         plocrveitem=pg.PlotCurveItem(pen=pg.mkPen(color))
    #         self.curveitems3.setdefault(name,(plocrveitem,np.array(self.newbarn_x)))
    #         self.myplot.addItem(self.curveitems3.get(name)[0])
    #
    # def addPoints2curves3(self,py=(0,)):
    #     """第三种方法，将Pipe加在这里"""
    #     if self.workon:
    #         self.newbarn.saveIn(py)
    #
    #
    #
    #
    # def PipeWork(self,index):
    #     """采样一条数据"""
    #     if self.workon:
    #         print"test"
    #         data = np.array(self.newbarn[index])
    #         tempPressure = data[:, 0]
    #         tempDistance = np.convolve(self.weight, data[:, 1],'Same')
    #         maxvalue=np.max(tempDistance)
    #         self.myplot.clear()
    #         self.curveitems3.get(0)[0].setData(x=np.array(self.curveitems3.get(0)[1]),
    #                                                 y=tempPressure)
    #         self.curveitems3.get(1)[0].setData(x=np.array(self.curveitems3.get(1)[1]),
    #                                           y=tempDistance)
    #         self.myplot.addItem(self.curveitems3.get(0)[0])
    #         self.myplot.addItem(self.curveitems3.get(1)[0])
    #         # self.Signal_showwindowForWidget.emit('MaxValue',str(maxvalue))
    #         self.newbarn.upDataIndex(index)



    #-------------控制类方法-------------------------

    def Close(self):
        self.workon=False
        print"绘图退出"

    def Slot_UpdataParas(self,value):
        self.Allpara=value
        print self.Allpara
        # print "-----",self.Allpara['电厂']



class CustomViewBox(pg.ViewBox):
    Signal_Vbox_rangechange = QtCore.pyqtSignal(int)
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        # self.setMouseMode(self.RectMode)
        self.Mode=0
        #0无法操作,1移动,2选择放大,3,还原

    ## reimplement right-click to zoom out
    def mouseClickEvent(self, ev):

        if ev.button() == QtCore.Qt.RightButton:
            self.autoRange()


    def mouseDragEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)

    def setModeParas(self,num):
        # print "--------------",num
        self.Mode=num
        if self.Mode==0:
            self.autoRange()
        elif self.Mode==1:
            self.setMouseMode(self.PanMode)
        elif self.Mode==2:
            self.setMouseMode(self.RectMode)
        elif self.Mode ==3:
            self.autoRange()
            self.Signal_Vbox_rangechange.emit(255)

    def setviewRange(self,y,auto=False):
        if auto==True:
            self.autoRange()
        else:
            self.setRange(yRange=y)








