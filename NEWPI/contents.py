#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os

reload(sys)
sys.setdefaultencoding('utf-8')#保证能够解码utf-8
#树莓派中使用时一定增添这个路径
sys.path.append("/home/pi/.local/lib/python2.7/site-packages")#不知道为什么找不到这个路径


from Loading import  FilesCheck
from  Five.Fothers.FiveLogging import  FiveLogbasic
from  Five.Fpyqtwidget import KeyBoard
from PyQt5 import QtCore, QtWidgets,QtGui
from  PyQt5.QtCore import  QThread,QTimer
from  login import loginOBJ
from  MianWindow import  MainWindowObj
from  DataControl import DataControlObj
from GetDatas import GetDataObj
from  Pipes import Pipe
log=FiveLogbasic("logs","./filecheck.log")






if __name__ =="__main__":
    filecheck=FilesCheck(log)#检查文件夹，文件，USB
    logintablepath=filecheck.FilesLists[1]
    if filecheck.CheckDirsFiles():
#所有类的示例化：
        app = QtWidgets.QApplication(sys.argv)
        #键盘实例化
        KeyboradInstance = KeyBoard.KeyBoard()#键盘
        #登录实例化
        Instance_Login = loginOBJ(Keyboard=KeyboradInstance,logintablePath=logintablepath)#登录
        #界面实例化
        Instance_Main=MainWindowObj(log=log,keyboard=KeyboradInstance,usb=filecheck.GetUsb())#主界面
        # 数据控制实例化，与加入线程管理
        DataControlInstance = DataControlObj(None)  # 数据控制实例
        Thread_DataControl = QThread()  # 数据控制线程
        DataControlInstance.moveToThread(Thread_DataControl)
        #数据处理管道实例化，与加入线程管理
        PipeInstance=Pipe(300,2)
        Thread_Pipe=QThread() #数据处理控制线程
        PipeInstance.moveToThread(Thread_Pipe)

        #数据获取实例化，与加入线程管理
        GetDataInstance=GetDataObj()#数据获取实例
        Thread_GetData=QThread()#数据获取线程
        GetDataInstance.moveToThread(Thread_GetData)

#模块之间各种信号的绑定
        #登录处与Main界面的信号绑定
        Instance_Login.Signal_infor.connect(Instance_Main.Slot_UserInfo_Region)#登录界面与主界面登录信号连接
        Instance_Main.Signal_Finish_Region.connect(Instance_Login.Slot_Fnish_Region)#结束登录界面的信号绑定
        #Main中与数据控制模块的信号绑定
        Instance_Main.Signal_SaveDirChanged_ForDB.connect(DataControlInstance.dataBasePathChanged)#绑定数据库路径，表更改
        Instance_Main.Signal_Pause.connect(DataControlInstance.SetPauseOrNot)#绑定暂停信号
        DataControlInstance.Sigal_DataBaseError.connect(Instance_Main.SlotMessageBox)#绑定错误提示
        Instance_Main.Signal_Close.connect(DataControlInstance.Close)#关闭数据控制模块的信号

        DataControlInstance.Sigal_QuerryData.connect(Instance_Main.SlotDealWithQuerryData)#数据控制返回的查询结果与数据处理的绑定
        Instance_Main.Signal_QuerrySQL.connect(DataControlInstance.QuerryData)#主界面数据查询与数据控制的查询的绑定
        Instance_Main.Signal_DelSQL.connect(DataControlInstance.DeleteData)
        #Main中与数据获取模块的信号绑定
        Instance_Main.Signal_SaveDirChanged_ForDB.connect(GetDataInstance.SetTableForSaving)#绑定数据库路径，表更改
        Instance_Main.Signal_Pause.connect(GetDataInstance.SetPauseOrNot)#绑定暂停信号
        GetDataInstance.Siganl_GetDatasError.connect(Instance_Main.SlotMessageBox)#绑定错误提示
        Instance_Main.Signal_Close.connect(GetDataInstance.Close)#关闭数据获取模块
        GetDataInstance.Siganl_ManagerWidget_ForGetData.connect(Instance_Main.SlotManagerWidget)#界面参数控制的信号绑定

        GetDataInstance.Signal_ForSaving.connect(DataControlInstance.InsertData)#数据插入的绑定
        GetDataInstance.Signal_Data2Window.connect(Instance_Main.ShiShiWindow.addPoints2curvesFIlter)#绑定界面绘图
        Instance_Main.Signal_SetWorkForAD.connect(GetDataInstance.SetWorkType)#数据获取模块的工作类型的设置
        Instance_Main.Signal_SetWhichForGetData.connect(GetDataInstance.SetWhichWays)#数据获取模块GetData的方式选择
        #数据获取模块工作时钟的设置
        Timer_ForGetData=QTimer()#操作数据获取模块总工作处的运行时间
        Timer_ForGetData.timeout.connect(GetDataInstance.Working)#计时器与工作信号绑定
        Timer_ForGetData.start(1)

        # 数据处理模块信号连接

        PipeInstance.Signal_outPipe_ForWindow.connect(Instance_Main.ShiShiWindow.addLines)#主界面绘图的连接
        GetDataInstance.Signal_ForPipes.connect(PipeInstance.inPipe)#数据获取模块的信号连接
        PipeInstance.Siganl_outPipe_ForWidget.connect(Instance_Main.SlotManagerWidget)#界面参数控制的信号绑定

        #数据控制线程启动
        Thread_DataControl.start()
        #数据获取线程启动
        Thread_GetData.start()
        #数据处理线程启动
        Thread_Pipe.start()

        #登录界面显示
        Instance_Login.show()

        sys.exit(app.exec_())


