#!/usr/bin/env python
# -*- coding: utf-8 -*-

from  Five.Fothers.FiveLogging import  FiveLogbasic
from Five.Fothers import FiveFileParser
import os



class FilesCheck(object):
    def __init__(self,log=None):
        if log==None:
            self.log=FiveLogbasic()
        else:
            self.log=log
        self.workpath = os.getcwd()
        self.BasePath = os.path.join(self.workpath, "GuanDian")
        self.DirsLists = ["SoftSetDir", "TemplateParaDir","ParasDir","SavingDir",]
        self.FilesLists=["".join([self.BasePath,"/",self.DirsLists[0],"/","setting.txt"]),
                         "".join([self.BasePath, "/", self.DirsLists[0], "/", "loginsetting.txt"]),
                         "".join([self.BasePath, "/", self.DirsLists[1], "/", "paratemplates.txt"]),
                         ]
        self.Savepath=os.path.join(self.BasePath, "SavingDir")
        self.usb=None

    def CheckDirsFiles(self):
        if self.CheckDirs():
            self.CheckFiles()
            self.CheckUsb()
        return  True

    def CheckDirs(self):
        """检查文件夹是否存在"""
        try:
            if not os.path.exists(self.BasePath):
                os.mkdir(self.BasePath)
            for dirs in self.DirsLists:
                path=os.path.join(self.BasePath,dirs)
                if not os.path.exists(path):
                    os.makedirs(path)
                    self.log.info("create dir:{}".format(path))
            return  True
        except:
            return False

    def GetUsb(self):
        return self.usb


    def CheckFiles(self):
        """检查文件是否存在"""
        try:
            for index,files in enumerate(self.FilesLists):
                files=os.path.normpath(files)
                if not os.path.exists(files):
                    with open(files,"w") as f:
                        self.log.info("create file:{}".format(files))
                        if index ==0:#"setting.txt"
                            FiveFileParser.writeComments(files,[r'saving*{}'.format(files)])
                        if index==1:
                            table={"省份名": "工厂名",
                                   }
                            FiveFileParser.insertTable(table,'regions',files,0)
                        if index==2:
                            table={"参数表名": "0", "电厂": "0",'阀门型号':"0",
                                   '整定压力':"0",'弹簧刚度':"0",'密封面内径':"0",
                                   '密封面外径':"0",'整调螺母方数':"0",
                                   }
                            FiveFileParser.insertTable(table,'MUBAN0',files,0)
                else:
                    if index==0:#"setting.txt"
                        FiveFileParser.updateComments(files,{'usb':r'{}'.format(self.Savepath)} )
            return True
        except Exception as e:
            return False



    def CheckUsb(self):
        """检查USB"""
        path=self.FilesLists[0]
        usb=FiveFileParser.getcomments(path,('usb',))['usb']
        if usb !=[]:#如果存在usb残留则删除记录
            FiveFileParser.removeComments(path,['usb'])
        FiveFileParser.writeComments(path,['usb*'])
        tempusb='None'#暂存usb的路径
        usbPATH = '/media/pi' #"/media/pi"#树莓派的Usb路径更改处
        if os.path.exists(usbPATH):
            if len(os.listdir(usbPATH)) != 0:
                for i in os.listdir(usbPATH):
                    if os.path.exists(os.path.join(usbPATH, i)):
                        tempusb=os.path.join(usbPATH, i)
                        self.usb = tempusb
                        break
        tempusb=self.Savepath if tempusb=='None' else tempusb
        FiveFileParser.updateComments(path,{'usb':r'{}'.format(tempusb)})





