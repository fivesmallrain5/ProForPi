#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from  PyQt5.QtCore import QObject
import os
from Five.Fothers import FivePath
from collections import  deque
import  sqlite3 as sq
import copy

#数据库里面表的表头
Biao='TIME , PRESSURE, DISTANCE'


class DataControlObj(QObject):
    dataBasePath=FivePath.join(os.getcwd(),["GuanDian","SavingDir"])#数据库的工作路径,用于copy的那个路径找不到时
    dataBaseName='database.db'#数据库名称
    pause_F=False#workloop中是否暂停数据库当前操作

    Sigal_DataBaseError=QtCore.pyqtSignal(str,str)#数据库传出的错误信息
    Sigal_QuerryData=QtCore.pyqtSignal(str,tuple)#发送来自哪里的查询，查询的数据结果

    def __init__(self,databasepath=None):
        super(DataControlObj, self).__init__()
        self.dataBasePath_copy=databasepath if databasepath is not None else copy.deepcopy(self.dataBasePath)
        #数据库的首次创建
        self.IsNewDaBase=True
        self.DataBaseCon=self.GetConnect()
        self.insertCount=0#用于什么时候提交事务
        self.ChoosedTable=False

#---------------------数据库维护性方法---------------------------------------
    def GetConnect(self):
        """返回一个连接"""
        try:
            if os.path.exists(os.path.join(self.dataBasePath_copy,self.dataBaseName)):
                self.IsNewDaBase=True
            else: self.IsNewDaBase=False
            con=sq.connect(os.path.join(self.dataBasePath_copy, self.dataBaseName),
                       timeout=5)
            return con
        except Exception  as e:
            self.Sigal_DataBaseError.emit('数据库错误',e.message)

    def SetPauseOrNot(self,flag):
        """设置标志位是否暂停对数据库的各种操作，可绑定暂定按钮"""
        self.pause_F=flag
        try:
            self.DataBaseCon.commit()
        except:
            pass


    def dataBasePathChanged(self,newpath,tablename):
        """一旦更改数据库的路径更改，就更新数据库的连接，创建新表"""
        try:
            self.pause_F=True
            self.dataBasePath_copy=newpath
            self.DataBaseCon=self.GetConnect()
            tablenames=self.GetTables()
            if tablename not in tablenames:
                self.CreateTable(para=[tablename,
                        'TIME INT PRIMARY KEY NOT NULL ,'
                        'PRESSURE REAL ,'
                        'DISTANCE REAL '])
            self.DataBaseCon.commit()
            self.ChoosedTable=True
            self.pause_F=False
        except Exception  as e:
            self.Sigal_DataBaseError.emit('数据库错误',e.message)



    def GetTables(self):
        """获取连接中的数据库的表"""
        try:
            cu = self.DataBaseCon.execute("select name from sqlite_master where type='table' order by name ")
            d = cu.fetchall()
            a = []
            for i in d:
                a.append(i[0])
        except:
            a=[]
        return a


    def Close(self):
        """关闭数据控制"""
        try:
            self.DataBaseCon.commit()
            self.DataBaseCon.close()
        except Exception:
            pass
        finally:
            print'结束数据库存储'



#------------------功能性质的函数--------------------------------------------
    def CreateTable(self,para):
        """创建数据表
        para[0], para[1]分别为表名，命令"""
        print "create table",para
        self.DataBaseCon.execute('''CREATE TABLE {} ({});'''.
                            format(para[0], para[1]))

    def InsertData(self,tablename,time,pressure,distance):
        """数据的插入,必须在进行dataBasePathChanged进行之后才会被激活"""
        try:
            if self.ChoosedTable and not self.pause_F:
                # print"insert"
                self.insertCount += 1
                self.DataBaseCon.execute('''INSERT INTO {} ({})VALUES ({})'''.
                    format(tablename,Biao," {} , {} , {} ".format(time,pressure,distance)))
                    #tablename,(TIME , PRESSURE, DISTANCE),时间数据，压力数据，位移数据
            if self.insertCount == 3000:#多久提交一次数据存储
                self.insertCount = 0
                self.DataBaseCon.commit()
        except Exception  as e:
            self.Sigal_DataBaseError.emit('数据库插入错误',e.message)



    def DeleteData(self,dataBasepath,sql):
        """删除数据"""
        try:
            newcon = sq.connect(os.path.join(dataBasepath, self.dataBaseName))
            newcon.execute(sql)
            newcon.close()
        except Exception as e:
            self.Sigal_DataBaseError.emit('数据删除错误', e.message)


    def QuerryData(self,commandFrom,dataBasepath,sql):
        """数据的查询,操作的优先级低于插入数据的优先级"""
        try:
            newcon=sq.connect(os.path.join(dataBasepath,self.dataBaseName))
            data=newcon.execute(sql).fetchall()
            self.Sigal_QuerryData.emit(commandFrom,tuple(data))
            newcon.close()
        except Exception as e:
            if 'block' in e.message:
                self.Sigal_DataBaseError.emit('数据表正在使用中',e.message)
            else:
                self.Sigal_DataBaseError.emit('数据库查询错误',e.message)









