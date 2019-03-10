#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys,os
#
sys.path.append("/home/pi/.local/lib/python2.7/site-packages")#不知道为什么找不到这个路径
from Loading import  FilesCheck
from  Five.Fothers.FiveLogging import  FiveLogbasic
from  Five.Fpyqtwidget import KeyBoard
from PyQt5 import QtCore, QtWidgets,QtGui
from  PyQt5.QtCore import  QThread,QTimer
from  login import loginOBJ
from  collections import deque
from itertools import  cycle
import numpy as np
import time
import  copy
import os
from  Five.Fothers import FiveFileParser
from  collections import  OrderedDict as Dict
from  Five.Fothers import FivePath
import Loading
import login,GetDatas,Pipes,ADS1120IPWR

from Five.Fpyqtwidget.F_Timer import MultipleQTimer as QTimerTable

try :
    # from forms.MainForm import Ui_MainWindow
    import pyqtgraph as pg
    print"hhh"
except Exception as e:
    print "message"
    print e.message
#from WindowShishi import ShowWindow


# from  MianWindow import  MainWindowObj
# from  DataControl import DataControlObj
# from GetDatas import GetDataObj
# from  Pipes import Pipe
log=FiveLogbasic("logs","./filecheck.log")
print sys.path
input("shuru ")