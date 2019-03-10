#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主要是界面显示部分
"""
from forms.MainForm import Ui_MainWindow
from PyQt5 import QtWidgets,QtCore,QtGui
from  Five.Fpyqtwidget.KeyBoard import KeyBoard
from Five.Fpyqtwidget.F_Timer import MultipleQTimer as QTimerTable
from  Five.Fothers import FiveFileParser
from  collections import  OrderedDict as Dict
from  Five.Fothers import FivePath
from WindowShishi import ShowWindow
from  collections import deque
from itertools import  cycle
import numpy as np
import time
import  copy
import os
import  threading
from Pipes import isnum


class MainWindowObj(QtWidgets.QMainWindow):
# --------------------所有的信号---------------------------------
    Signal_Finish_Region=QtCore.pyqtSignal()#关闭登录界面
    Signal_Close=QtCore.pyqtSignal()#关闭
    Signal_Pause=QtCore.pyqtSignal(bool)#暂停所有操作
    Siganl_ManagerWidget=QtCore.pyqtSignal(str,str)#管理界面的一些变化较大的控件的信号
    Signal_SaveDirChanged=QtCore.pyqtSignal(str)#数据保存路径更改,发送新的路径
    Signal_SaveDirChanged_ForDB=QtCore.pyqtSignal(str,str)#数据保存路径更改,发送新的路径,表名
    Signal_Xiu_Tools=QtCore.pyqtSignal(int,bool)#修改参数表数据表处显示那种工具
    Signal_UseThisParaTable=QtCore.pyqtSignal(str)#选择参数后，str为数据表名
    Signal_QuerrySQL=QtCore.pyqtSignal(str,str,str)#查询数据库数据的信号，谁发出的查询，数据库路径，SQL语句
    Signal_SetWorkForAD=QtCore.pyqtSignal(str,str)#设置数据获取模块执行的工作

    Signal_DelSQL=QtCore.pyqtSignal(str,str)#删除数据库表，数据库路径，SQL语句
    Signal_SetWhichForGetData=QtCore.pyqtSignal(bool)#设置获取数据模块数据的获取方式
    Signal_UpdataParas=QtCore.pyqtSignal(dict)#更新所选择参数表
# --------------------所有的沟通性质的信号槽-------------------------
    def Slot_UserInfo_Region(self,region,gen):
        """处理登录界面传来的信息"""
        self.log.info("login:{} {}".format(region,gen))
        self.Signal_Finish_Region.emit()
        self.show()
        # self.showFullScreen()  # 全屏模式
        self.showMaximized()
        self.Siganl_ManagerWidget.emit('user',gen)



# --------------------主要方法------------------------
    def __init__(self,log=None,keyboard=None,database= None,usb=None):
        #变量初始化
        super(MainWindowObj,self).__init__()
        self.Allpara=dict()#保存参数表里面的参数，这个才是真正的用于各种计算的参数
        #其他模块也有这个参数ALLpara,这个模块的参数一旦变换，所有模块的这个参数都会变化
        self.UI = Ui_MainWindow()
        self.UI.setupUi(self)  # 加载界面
        self.log=log
        self.DataBase=database#数据库
        self.keyboard=keyboard
        self.TemplateParaDir=FivePath.join(os.getcwd(),['GuanDian','TemplateParaDir'])
        self.ParasDir = FivePath.join(os.getcwd(),['GuanDian', 'ParasDir'])

        self.SavingDir=FivePath.join(os.getcwd(),['GuanDian','SavingDir'])
        self.AnotherSavingDir=usb#USB,更改数据保存路径只修改这个保存路径副本
        if self.AnotherSavingDir is  None:
            self.AnotherSavingDir=copy.deepcopy(self.SavingDir)
        #信号与槽的绑定
        self.Signal_SaveDirChanged.connect(self.SlotSavingFileChanged)
        self.Signal_Xiu_Tools.connect(self.SlotConrtrolTools)
        self.Signal_UpdataParas.connect(self.Slot_UpdataParas)  # Allpara的值的信号与槽的绑定
        # 初始化信号发射
        self.Signal_Xiu_Tools.emit(-1,False)

        #所用的初始函数
        self.InitZhujiemian()
        self.InitMangerWidget()
        self.InitTianJiaCanShu()
        self.InitXiuGaiCanShu()
        self.InitYongHuShezhi()
        self.InitShiShiHuiTu()
        self.InitZaiRuJieGuo()
        self.CMDPartInit()



# --------------------主界面--------开始-------------------------
    def InitZhujiemian(self):
        self.setWindowTitle('光电实验室')
        self.Green = cycle(["QPushButton {  background-color: rgb(85, 255, 0) ;border-radius:15px;}\n",
                            "QPushButton {  background-color: rgb(127, 127, 127) ;border-radius:15px;}\n"])
        self.Red = cycle(["QPushButton {  background-color: rgb(255, 23, 7) ;border-radius:15px;}\n",
                          "QPushButton {  background-color: rgb(127, 127, 127) ;border-radius:15px;}\n"])
        self.Linking = False
        #函数设置
        self.SetPower()
        self.SetLink()
        #信号槽绑定
        self.UI.Z_PB_StartMeasure.clicked.connect(self.SlotPushbutton_StartMeasure)
        self.UI.Z_PB_StopMeasure.clicked.connect(self.SlotPushbutton_StopMeasure)
        self.UI.PB_CLOSE_SOFT.clicked.connect(self.safeClose)
        #界面灯闪烁用的时钟以及电压，连接获取的时钟
        self.InerTimer = QTimerTable(self)
        self.InerTimer.addTimeEvent(1,self.Starslink,-1)#常闪烁
        self.InerTimer.addTimeEvent(3,self.ForTimer_getLink,5)#只执行5次获取连接
        self.InerTimer.addTimeEvent(400, self.ForTimer_getLink, -1)#每4分钟获取一次连接
        self.InerTimer.addTimeEvent(5,self.ForTimer_getPower,5)#只执行5次获取电压
        self.InerTimer.addTimeEvent(600,self.ForTimer_getPower,-1)#每6分钟获取一次电压
        self.InerTimer.timeout.connect(self.InerTimer.executeTable)
        self.InerTimer.start(600)
        pass
    def ForTimer_getPower(self):
        self.Signal_SetWorkForAD.emit('Power','False')

    def ForTimer_getLink(self):
        self.Signal_SetWorkForAD.emit('Link','False')


    def SetPower(self, value=1):
        """电压设置"""
        if value <= 20:
            self.UI.L_Battery.setPixmap(QtGui.QPixmap("./resource/b1.png"))
        elif value <= 50:
            self.UI.L_Battery.setPixmap(QtGui.QPixmap("./resource/b2.png"))
        elif value <= 80:
            self.UI.L_Battery.setPixmap(QtGui.QPixmap("./resource/b3.png"))
        elif value > 90:
            self.UI.L_Battery.setPixmap(QtGui.QPixmap("./resource/b4.png"))

    def SetLink(self,value=False):
        """连接设置"""
        self.Linking=value

    def Starslink(self):
        """连接灯闪烁"""
        if self.Linking:
            self.UI.LED.setStyleSheet(self.Green.next())
        else:
            self.UI.LED.setStyleSheet(self.Red.next())

    def SlotPushbutton_StartMeasure(self):
        """开始测量按钮发送"""
        self.Signal_Pause.emit(False)
        self.Signal_Pause.emit(False)
        self.Siganl_ManagerWidget.emit('TongZhi','\n开始测量')
        self.Signal_SetWorkForAD.emit('M_Data','True')

    def SlotPushbutton_StopMeasure(self):
        """停止测量按钮发送"""
        self.Signal_Pause.emit(True)
        self.Signal_Pause.emit(True)
        self.Siganl_ManagerWidget.emit('TongZhi', '\n停止测量')
        self.Signal_SetWorkForAD.emit('None','True')


# --------------------主界面---------结束-------------------




# --------------------添加参数--------开始-------------------------
    def InitTianJiaCanShu(self):
        self.parefile={'row':6,'col':4}#添加参数表的行列
        self.UI.table_tianjiacanshu.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)
        self.UI.table_tianjiacanshu.verticalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)
        self.SetTableRowCol_TJCS(self.parefile['row'],self.parefile['col'])
        self.UI.table_tianjiacanshu.verticalHeader().setHidden(True)
        self.UI.table_tianjiacanshu.horizontalHeader().setHidden(True)
        table=os.path.join(self.TemplateParaDir,'paratemplates.txt')
        self.CreateTable_TJCS(table)
        self.keyboard.InstallCallBackFuns(2,self.SetKB_Num_Table_TJCS)
        self.UI.table_tianjiacanshu.cellClicked.connect(self.SlotCellClicked_TJCS)
        self.UI.T_PB_SavePara.clicked.connect(self.SlotPushbutton_Save_TJCS)
        self.UI.pb_ChooseNewTem.clicked.connect(self.SlotPushbutton_NewTemps)
        pass

    def SetTableRowCol_TJCS(self,row,col):
        """表的格数设置"""
        self.UI.table_tianjiacanshu.setColumnCount(col)
        self.UI.table_tianjiacanshu.setRowCount(row)

    def CreateTable_TJCS(self,table):
        """创建参数表"""
        temp= FiveFileParser.readTable(table)
        self.UI.table_tianjiacanshu.clear()
        if temp  is not None:
            temp=Dict(temp[temp.keys()[0]]['cellContent'])
            self.tableinfor = Dict()
            row, col = CalculateRowCol(temp.keys())
            self.parefile['row'], self.parefile['col']=row,col
            self.SetTableRowCol_TJCS(row,col)
            self.tableinfor.setdefault('存储为','MUBAN')
            for data in temp.iteritems():
                self.tableinfor.setdefault(data[0],data[1])
            for i,data in enumerate(self.tableinfor.iteritems()):
                item = QtWidgets.QTableWidgetItem()
                item.setText(data[0])
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.UI.table_tianjiacanshu.setItem(i % self.parefile['row'], (i // self.parefile['row']) * 2, item)
        else:
            self.tableinfor=Dict()
            self.tableinfor.setdefault('存储为', 'MUBAN')
#
    def SlotCellClicked_TJCS(self, row, colum):
        """表格中点击处理"""
        if colum % 2.0 != 0:
            self.keyboard.setTag(2)
            self.keyboard.clearAllNotTag()
            self.keyboard.show()
            self.keyboard.setattachInfo((row,colum))


    def SetKB_Num_Table_TJCS(self,text,priority,tag,attach):
        """将点击后按键的数据传会表上"""
        if attach !=None:
            item = QtWidgets.QTableWidgetItem()
            item.setText(text)
            self.UI.table_tianjiacanshu.setItem(attach[0],attach[1],item)
            self.tableinfor[self.tableinfor.keys()[attach[0]+(attach[1]//2)*self.parefile['row']]]=text


    def SlotPushbutton_Save_TJCS(self):
        """保存参数处保存按钮"""
        file=self.tableinfor[self.tableinfor.keys()[0]]#文件名
        path=os.path.join(self.ParasDir,file)
        while os.path.exists("".join([path,'.txt'])):
            path="".join([path,'_backup'])
        temp = copy.deepcopy(self.tableinfor)
        temp.popitem(False)#
        temp=dict(temp)
        FiveFileParser.createTable("".join([path,'.txt']))
        FiveFileParser.insertTable(temp,'MUBAN',"".join([path,'.txt']),0)
        QtWidgets.QMessageBox.information(self,'提示','保存为：\n'
                '{}'.format("".join([path,'.txt'])),QtWidgets.QMessageBox.Yes)



    def SlotPushbutton_NewTemps(self):
        """选择新的参数模版"""
        path = QtWidgets.QFileDialog.getOpenFileName(self, "选择参数模板",
                            self.TemplateParaDir)
        path=path[0]
        self.CreateTable_TJCS(path)
# --------------------添加参数--------结束-------------------------



# --------------------修改参数--------开始-------------------------
    def InitXiuGaiCanShu(self):
        self.tableinfor_2=None#用于存储当前table中数据
        self.tableinfor_2Save=None#保存table中数据时用的
        self.currentfilepath=None#当前表的路径{'path':path参数列表,'type':0参数列表,1数据列表,}
        self.ParaModel=QtWidgets.QFileSystemModel()#文件模型
        self.ParaModel.setRootPath(os.getcwd())
        self.SaveModel=QtWidgets.QFileSystemModel()#文件模型
        namefilter=['*.txt','*.d']
        self.SaveModel.setNameFilterDisables(False)
        self.SaveModel.setNameFilters(namefilter)
        self.SaveModel.setRootPath(os.getcwd())
        #参数列表的模型设立
        self.UI.CanshuList_2.setModel(self.ParaModel)
        self.UI.CanshuList_2.setRootIndex(self.ParaModel.index(self.ParasDir))
        self.UI.CanshuList_2.clicked.connect(self.CreateTableFomParas)
        #数据列表的模型设立
        self.UI.ShujuList_2.setModel(self.SaveModel)
        self.UI.ShujuList_2.setRootIndex(self.SaveModel.index(self.AnotherSavingDir))
        self.UI.ShujuList_2.clicked.connect(self.CreateTableFomDatas)
        #table的配置
        self.UI.tableWidget.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)
        self.UI.tableWidget.verticalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)
        self.SetTableRowCol_CGCS(6,4)
        self.UI.tableWidget.verticalHeader().setHidden(True)
        self.UI.tableWidget.horizontalHeader().setHidden(True)
        #键盘设置
        self.keyboard.InstallCallBackFuns(3, self.SetKB_Num_Table_CGCS)
        self.UI.tableWidget.cellClicked.connect(self.SlotCellClicked_CGCS)
        self.UI.pb_SaveChange.clicked.connect(self.SlotPushbutton_Save_CGCS)
        pass
        #toolbox处的配置
        self.UI.toolBox.currentChanged.connect(self.SlotConrtrolTools)
        self.UI.toolBox.currentChanged.emit(self.UI.toolBox.currentIndex())
        self.UI.pb_CGCS_del_canshu.clicked.connect(self.SlotPushbutton_DeleteTable_CGCS)#删除参数表
        self.UI.pb_delData_CGCS.clicked.connect(self.SlotPushbutton_DeleteTable_CGCS)#删除数据表
        self.UI.pb_ok_Para.clicked.connect(self.SlotPushbutton_UseThisPara)#使用该参数
        self.UI.pbCGCS_watch_data.clicked.connect(self.SlotPushbutton_WatchData_CGCS)#查看数据
        self.UI.pb_export.clicked.connect(self.SlotPushbutton_ExportData_CGCS)#导出数据

    def CreateTableFomParas(self,index):
        """从参数列表创建表格"""
        path=self.ParaModel.filePath(index)
        if not self.ParaModel.isDir(index):
            self.currentfilepath = {'path':path,'type':0,}
            self.CreatTable_CGCS(path,0)
    def CreateTableFomDatas(self,index):
        """从参数列表创建表格"""
        path=self.ParaModel.filePath(index)
        if not self.ParaModel.isDir(index):
            self.currentfilepath = {'path':path,'type':1,}
            self.CreatTable_CGCS(path,1)

    def SetTableRowCol_CGCS(self,row,col):
        """表的格数设置"""
        self.UI.tableWidget.setColumnCount(col)
        self.UI.tableWidget.setRowCount(row)

    def ClearTable_CGCS(self):
        """清除表"""
        self.UI.tableWidget.clear()
    def CreatTable_CGCS(self,tablepath,type=0):
        """修改参数界面的表格绘制函数"""
        self.tableinfor_2 = FiveFileParser.readTable(tablepath)
        self.UI.tableWidget.clear()
        if self.tableinfor_2  is not None:
            self.tableinfor_2=Dict(self.tableinfor_2[self.tableinfor_2.keys()[0]]['cellContent'])
            self.tableinfor_2Save = copy.deepcopy(self.tableinfor_2)#获取存储数据
            row,col=CalculateRowCol(self.tableinfor_2.keys())
            self.currentfilepath.setdefault('row',row)
            self.currentfilepath.setdefault('col',col)
            self.SetTableRowCol_CGCS(row,col)#更新表格的个数
            for i,data in enumerate(self.tableinfor_2.iteritems()):
                itemkey = QtWidgets.QTableWidgetItem()
                itemvalue=QtWidgets.QTableWidgetItem()
                if type==0:
                    itemkey.setBackground(QtGui.QBrush(QtGui.QColor(200, 184, 7)))
                else:
                    itemkey.setBackground(QtGui.QBrush(QtGui.QColor(188, 229, 255)))
                itemkey.setText(data[0])
                itemvalue.setText(data[1])
                itemkey.setFlags(QtCore.Qt.ItemIsEnabled)
                self.UI.tableWidget.setItem(i % self.currentfilepath['row'],
                                (i // self.currentfilepath['row']) * 2, itemkey)
                self.UI.tableWidget.setItem(i%self.currentfilepath['row'],(i // self.currentfilepath['row']) * 2+1,itemvalue)
        else:
            self.tableinfor_2=None


    def SlotConrtrolTools(self,whichtool=-1,Flag=True):
        """控制修改参数处工具的显示"""
        self.ClearTable_CGCS()
        if whichtool==0:
            if Flag:
                self.UI.frame_canshu.show()
                self.UI.frame_shuju.hide()
            else:
                self.UI.frame_canshu.hide()
        elif whichtool==1:
            if Flag:
                self.UI.frame_shuju.show()
                self.UI.frame_canshu.hide()
            else:
                self.UI.frame_shuju.hide()
        else:
            self.UI.frame_shuju.hide()
            self.UI.frame_canshu.hide()


    def SlotCellClicked_CGCS(self, row, colum):
        """表格中点击处理"""
        if colum % 2.0 != 0 and self.UI.toolBox.currentIndex()==0:
            self.keyboard.setTag(3)
            self.keyboard.clearAllNotTag()
            self.keyboard.show()
            self.keyboard.setattachInfo((row, colum,3))


    def SetKB_Num_Table_CGCS(self, text, priority, tag, attach):
        """将点击后按键的数据传会表上"""
        if attach[2] ==3:
            item = QtWidgets.QTableWidgetItem()
            item.setText(text)
            self.UI.tableWidget.setItem(attach[0], attach[1], item)
            self.tableinfor_2Save[self.tableinfor_2Save.keys()[attach[0] +(attach[1]//2)*self.currentfilepath['row']]]=text

    def SlotPushbutton_Save_CGCS(self):
        """保存按钮信号槽，用于保存修改的数据"""
        if self.currentfilepath is not None and self.currentfilepath['type']==0:
            FiveFileParser.updataTable(dict(self.tableinfor_2Save),'MUBAN',
                                       self.currentfilepath['path'])
            QtWidgets.QMessageBox.information(self, '提示', '更改成功：'
                                        '{}'.format(os.path.split(self.currentfilepath['path'])[1]),
                                        QtWidgets.QMessageBox.Yes)

    def SlotPushbutton_DeleteTable_CGCS(self):
        """用与删除当前self.currentfilepath变量对应的表"""
        if self.currentfilepath is not None:
            if self.currentfilepath['type'] == 1:#如果是数据表就删除，而且数据库中对应的也删除
                infor = FiveFileParser.getcomments(self.currentfilepath['path'], ('DataTable', 'DataBaseDir'))
                name = infor['DataTable'][0].rstrip('\n')
                path = infor['DataBaseDir'][0].rstrip('\n')
                self.Signal_DelSQL.emit( path, ' DROP TABLE {} '.format(name))
            os.remove(self.currentfilepath['path'])
            QtWidgets.QMessageBox.information(self, '提示', '删除成功：'
                                               '{}'.format(os.path.split(self.currentfilepath['path'])[1]),
                                              QtWidgets.QMessageBox.Yes)
            self.log.info('delete file:  {}'.format(self.currentfilepath['path']))
            self.ClearTable_CGCS()

    def SlotPushbutton_ExportData_CGCS(self):
        """导出数据"""
        if self.currentfilepath is  not None and self.currentfilepath['type']==1:
            # self.UI.tabWidget.setCurrentIndex(3)
            #创建文件夹
            basepath, exname = os.path.split(self.currentfilepath['path'])
            filename, suffix = os.path.splitext(exname)
            if not os.path.exists(os.path.join(self.AnotherSavingDir, filename)):#创建文件夹
                os.mkdir(os.path.join(self.AnotherSavingDir, filename))

            infor=FiveFileParser.getcomments(self.currentfilepath['path'],('DataTable','DataBaseDir'))
            name=infor['DataTable'][0].rstrip('\n')
            path=infor['DataBaseDir'][0].rstrip('\n')
            self.Signal_QuerrySQL.emit('ex*{}*{}'.format(self.currentfilepath['path'],os.path.join(self.AnotherSavingDir, filename)),
                                       path,' select PRESSURE , DISTANCE from {}  '.format(name))
            self.log.info('export data :{},{}'.format(path,name))

        pass
#-----------------
# #数据库查询的地方就更在查询信号的
# #sql语句和处理返回的SlotDealWithQuerryData--------------------
    def SlotPushbutton_WatchData_CGCS(self):
        """查看数据"""
        if self.currentfilepath is  not None and self.currentfilepath['type']==1:
            self.UI.tabWidget.setCurrentIndex(3)
            infor=FiveFileParser.getcomments(self.currentfilepath['path'],('DataTable','DataBaseDir'))
            name=infor['DataTable'][0].rstrip('\n')
            path=infor['DataBaseDir'][0].rstrip('\n')
            self.Signal_QuerrySQL.emit('cs',
                                       path,' select PRESSURE  from {}  '.format(name))
            self.log.info('querry data :{},{}'.format(path,name))

    def SlotDealWithQuerryData(self,where,data):
        """处理来自数据库查询的数据"""
        if where.startswith('cs'):#处理数据发出的用于绘图的数据
            try:
                if data!=():
                    data = np.array(data)[:, 0]
                    self.ZaiRuWindow.addLines((0,),(tuple(data),),('r',))
                else:
                    self.SlotMessageBox('错误！','此表无数据！')
            except:
                pass
            print '来自数据库的数据'
        elif where.startswith('ex*'):#处理数据发出的用于导出的数据
            where=where.lstrip('ex*')#去除信息前缀
            oldfilepath,newfiledir=where.split('*')#来自哪个数据表，数据应该存储的位置
            infor = FiveFileParser.readTable(oldfilepath)
            infor=infor[infor.keys()[0]]['cellContent']#获取文件中的表
            temppath=os.path.split(oldfilepath)[1]#获取文件名
            temppath=temppath.replace('.d','.txt')#替换文件后缀名
            with open(os.path.join(newfiledir,temppath),'w') as f:#创建数据文件
                pass
            #首先存储参数表
            FiveFileParser.insertTable(infor,'所使用参数',os.path.join(newfiledir,temppath),-1)
            #创建线程来存数数据
            fd=threading.Thread(target=saveData2File,args=(os.path.join(newfiledir,temppath),data))
            fd.start()
            self.SlotMessageBox('提示','数据导出成功！')







    def SlotPushbutton_UseThisPara(self):
        """设置使用该参数列表"""
        if self.tableinfor_2Save!=self.tableinfor_2:#保存修改后的参数
            if self.currentfilepath is not None and self.currentfilepath['type'] == 0:
                FiveFileParser.updataTable(dict(self.tableinfor_2Save), 'MUBAN',
                                           self.currentfilepath['path'])
        self.Signal_UpdataParas.emit(dict(self.tableinfor_2Save))
        #创建数据表（包含参数，用一个data来存数据在数据库中的位置）
        #当前参数表对应的名字，不要后缀
        name="D"+os.path.split(self.currentfilepath['path'])[1].rstrip('.txt')+"时间"+time.strftime('%Y%m%d%M',time.localtime())
        #检测当前名字是否合适
        while os.path.exists("".join([os.path.join(self.AnotherSavingDir,name),'.d'])):
            name+='cp'
        #数据表路径
        path=os.path.join(self.AnotherSavingDir,''.join([name,'.d']))#数据表后缀变为‘.d’
        FiveFileParser.createTable(path)
        FiveFileParser.insertTable(dict(self.tableinfor_2Save), '参数',path,0)
        FiveFileParser.writeComments(path,'\nDataBaseDir*{}\nDataTable*{}'.format(self.AnotherSavingDir,name))
        QtWidgets.QMessageBox.information(self, '提示', '参数选择成功：'
                                          '数据表为：{}\n立即搜集数据'.format(name),
                                          QtWidgets.QMessageBox.Yes)
        self.Signal_SaveDirChanged_ForDB.emit(self.AnotherSavingDir,name)
        self.Signal_UseThisParaTable.emit(name)
        self.Siganl_ManagerWidget.emit('ShuJuBiao',''.join(name))
        self.log.info('Create DataTable:  {}.d'.format(name))

# --------------------修改参数--------结束-------------------------






# --------------------载入结果--------开始-------------------------
    def InitZaiRuJieGuo(self):
        self.ZaiRuWindow=ShowWindow(self.UI.graphicsView_2)
        self.ZaiRuWindow.workon=True
        #载入界面功能按键的设置
        self.UI.Z_PB_DEFAULT_4.clicked.connect(self.setModePB_DEFAULT)
        self.UI.Z_PB_MOVE_4.clicked.connect(self.setModePB_MOVE)
        self.UI.Z_PB_SlectBigger_4.clicked.connect(self.setModePB_SlectBigger)
        self.UI.Z_PB_MAX_4.clicked.connect(self.setModePb_MAX)


     # ------------------------------载入结果界面部分按键的作用设置

    def setModePB_DEFAULT(self):
        # print "DEFAULT"
        self.ZaiRuWindow.viewbox.setModeParas(3)

    def setModePB_MOVE(self):
        # print "_MOVE"
        self.ZaiRuWindow.viewbox.setModeParas(1)

    def setModePB_SlectBigger(self):
        # print "SlectBigger"
        self.ZaiRuWindow.viewbox.setModeParas(2)

    def setModePb_MAX(self):
        self.ZaiRuWindow.viewbox.setModeParas(0)
# --------------------载入结果--------结束-------------------------





# --------------------实时绘图--------开始-------------------------
    def InitShiShiHuiTu(self):
        self.UI.Z_CB_OpenShiShi_2.setChecked(False)
        self.ShiShiWindow=ShowWindow(self.UI.graphicsView)
        self.ShiShiWindow.setCurves((0,1),('r','g'))#实时绘图窗口的控制
        self.Signal_UpdataParas.connect(self.ShiShiWindow.Slot_UpdataParas)  # 绑定主界面更改参数信号与绘图界面的更改参数
        self.ShiShiWindow.Signal_showwindowForWidget.connect(self.SlotManagerWidget)
        self.UI.Z_CB_OpenShiShi_2.clicked.connect(self.whichWayforGetData)
        self.UI.pb_huitukaiqi_2.clicked.connect(self.allowDraw)

        #控制绘图界面的范围
        self.UI.y_min_3.clicked.connect(self.showkeyboardFormin)
        self.UI.y_max.clicked.connect(self.showkeyboardFormax)
        self.keyboard.InstallCallBackFuns(9,self.setTextFormin)#键盘
        self.keyboard.InstallCallBackFuns(10, self.setTextFormax)
        self.UI.Z_PB_DEFAULT_3.clicked.connect(self.setdefaultwindow)

        self.OpenShishi = True
        self.ShiShiWindow.workon = self.OpenShishi


    def allowDraw(self):
        """实时绘图的开关"""
        self.OpenShishi = not self.OpenShishi
        self.ShiShiWindow.workon=self.OpenShishi


    def whichWayforGetData(self):
        """绘图显示的方式"""
        if self.UI.Z_CB_OpenShiShi_2.isChecked():
            self.ShiShiWindow.myplot.clear()
            self.ShiShiWindow.workon = False
            self.Signal_SetWhichForGetData.emit(True)
            self.Signal_SetWhichForGetData.emit(True)
            self.Signal_SetWhichForGetData.emit(True)
            self.Signal_SetWhichForGetData.emit(True)
            self.ShiShiWindow.workon = True
        else:
            self.ShiShiWindow.myplot.clear()
            self.ShiShiWindow.workon = False
            self.Signal_SetWhichForGetData.emit(False)
            self.Signal_SetWhichForGetData.emit(False)
            self.Signal_SetWhichForGetData.emit(False)
            self.ShiShiWindow.workon = True

    def showkeyboardFormin(self):
        """设置y轴最小值"""
        self.keyboard.setTag(9)
        self.keyboard.show()
        self.keyboard.clearAllNotTag()

    def showkeyboardFormax(self):
        """设置y轴最大值"""
        self.keyboard.setTag(10)
        self.keyboard.show()
        self.keyboard.clearAllNotTag()

    def setTextFormin(self,text, priority, tag, attach):

        if tag ==9 and priority==1:
            if isnum(text):
                self.UI.y_min_3.setText(text)
                if isnum(self.UI.y_max.text()):
                    try:
                        min, max = float("".join(self.UI.y_min_3.text()).strip()), float(
                            "".join(self.UI.y_max.text()).strip())
                        # min,max=float(self.UI.y_min_3.text()),float(self.UI.y_max.text())
                        self.ShiShiWindow.viewbox.setviewRange((min, max))
                    except:
                        pass
            else:
                self.UI.y_min_3.setText("")

    def setTextFormax(self, text, priority, tag, attach):
        # try:
            text=text.strip()
            if tag == 10 and priority == 1:
                if isnum(text):
                    self.UI.y_max.setText(text)
                    if isnum(self.UI.y_min_3.text()):
                        try:
                            min,max=float("".join(self.UI.y_min_3.text()).strip()),float("".join(self.UI.y_max.text()).strip())
                            self.ShiShiWindow.viewbox.setviewRange((min, max))
                        except:
                            pass

                else:
                    self.UI.y_max.setText("")


    def setdefaultwindow(self):
        self.ShiShiWindow.viewbox.setviewRange((0,0))




# --------------------实时绘图--------结束-------------------------

#-------------------用户设置--------开始-------------------------
    def InitYongHuShezhi(self):
        #存储路径的设置
        self.Siganl_ManagerWidget.emit('SavePath', self.AnotherSavingDir)
        self.UI.PB_WorkPath.clicked.connect(self.SlotPb_saveChange_YHSZ)
        pass

    def SlotPb_saveChange_YHSZ(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择保存路径",
                            self.SavingDir, QtWidgets.QFileDialog.ShowDirsOnly)
        if os.path.exists(path):
            self.AnotherSavingDir=path
            self.SlotSavingFileChanged(path)

# --------------------用户设置--------结束-------------------------


# --------------------辅助功能--------开始-------------------------
    """变化较大的一些控件，或者其他模块想在主界面的控件显示一些信息，
        操作主界面的方法可以使用下面的这种方法
      使用Siganl_ManagerWidget信号传送信息
    """

    def InitMangerWidget(self):
        self.MessageBoxLine=deque(maxlen=5)
        self.M_WidgetDict={'user':[self.UI.Z_LB0],#主界面用户
                           'ZhengDingYali':[self.UI.Z_LB4],#主界面整定压力
                           'TiShengLi':[self.UI.Z_LB_TiShengLi],#
                           'ShuJuBiao':[self.UI.Z_SHUJUBIAO],#主界面数据表
                           'SavePath':[self.UI.LE_WorkPath],#用户设置的存储路径
                           'TongZhi':[self.UI.Z_TB0],#主界面的通知
                           'MaxValue':[self.UI.SH_LB_32]#实时绘图的最大值
                           }
        self.M_MethodDict={'Link':self.SetLink,
                           'Power':self.SetPower,
                          }
        self.Siganl_ManagerWidget.connect(self.SlotManagerWidget)
        pass

    def SlotManagerWidget(self,name,value):
        """管理所有会有同值的控件"""
        if name in self.M_WidgetDict.keys():
            for wids in self.M_WidgetDict[name]:
                if wids.inherits('QLabel'):#QLable类进行同种操作
                    wids.setText(value)
                elif wids.inherits('QLineEdit'):
                     wids.setText(value)
                elif wids.inherits('QTextBrowser'):
                    if value.startswith('html:'):
                        value=value.lstrip('html:')
                        wids.setHtml(value)
                    else:
                        wids.setPlainText(value)
                else:
                    pass
        elif name in self.M_MethodDict.keys():
            if name=='Link':#控制主界面连接的地方
                value=False if value=='False' else True
                self.M_MethodDict[name](value)
            elif name=='Power':#设置主界面电量的显示
                try:
                    value=int(value)
                except Exception:
                    value=0
                self.M_MethodDict[name](value)
            pass

    def Slot_UpdataParas(self,value):
        self.Allpara=value


    """全局可能用到的一些函数"""
    def SlotSavingFileChanged(self,newpath):
        if self.AnotherSavingDir is  None:
            self.AnotherSavingDir=copy.deepcopy(self.SavingDir)
        else:
            self.AnotherSavingDir=newpath
        #更新数据列表处的数据
        self.UI.ShujuList_2.setRootIndex(self.SaveModel.index(self.AnotherSavingDir))
        self.Siganl_ManagerWidget.emit('SavePath',self.AnotherSavingDir)

    def SlotMessageBox(self,topic,strs):
        """用于其他模块出现错误时，进行弹窗提示"""
        if self.MessageBoxLine.count(strs)<3:
            print strs
            self.MessageBoxLine.append(strs)#当同样的错误信息出现超过5次以后就不弹窗了
            QtWidgets.QMessageBox.information(self, topic,strs,
                    QtWidgets.QMessageBox.Yes)

    def closeEvent(self, *args, **kwargs):#退出时间，按主界面的‘叉’会主动调用
        self.Signal_Close.emit()
        self.ZaiRuWindow.Close()
        self.ShiShiWindow.Close()

    def safeClose(self ):#主界面的关闭按钮，这个更安全，保证各种信号会被接收
        self.Signal_Close.emit()
        self.ZaiRuWindow.Close()
        self.ShiShiWindow.Close()
        QtWidgets.QApplication.quit()


    #---------------------------CMD-------------------------


    def CMDPartInit(self):
        self.UI.CMD_INPUT.clicked.connect(self.CmdInputclick)
        self.UI.CMD_ENTER.clicked.connect(self.CmdEnterclick)
        self.keyboard.SignalALLmessage.connect(self.CmdInputChangeContent)
        self.Command = ""

    def CmdInputclick(self):
        self.keyboard.setTag(112)
        self.keyboard.clearAllNotTag()
        self.keyboard.show()
        self.Commands={"sn":self.showNormal ,"help":self.CmdHelp,"h":self.CmdHelp,"clear":self.UI.CMD_TERMINAL.clear}
        pass


    def CmdInputChangeContent(self, st, types, tags):
        """Cmd表中当单元格被点击时"""
        if tags == 112:
            self.UI.CMD_TERMINAL.insertPlainText("\n@admin:{}".format(st))
            self.Command = st

    def CmdEnterclick(self):
        if self.Command !="":
            if self.Commands.has_key(self.Command):
                self.Commands[self.Command]()
            else:
                self.UI.CMD_TERMINAL.insertPlainText("\n>>>{}".format("Command error!"))
                pass


    def CmdHelp(self):
        self.UI.CMD_TERMINAL.insertPlainText(
            "\n>>>command:\n\tsn:Screen nomalize"
            "\n\th help :show all commands\n\t"
             "\n\tclear:clear all\n\t"
            "shutdown:close\n"
        )


#--------------------一些函数------------------

def CalculateRowCol(lists):
    """计算表的行列"""
    return len(lists)//2+1,4



def saveData2File(path,data):
    """将一个tuple的数据存储成文件，要更改数据存储形式在这里更改"""
    with open(path,'a+') as f:
        try:
            f.write("\n数据：序号\t压力\t位移\n")
            for index, i in enumerate(data):
                f.write("{} {} {}\n".format(index,i[0],i[1]))
        except:
            f.write('无数据！')
    print "存储结束"


# --------------------辅助功能--------结束-------------------------


