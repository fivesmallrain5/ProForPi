#!/usr/bin/env python
# -*- coding: utf-8 -*-

""""
v=2
与之前的keyBoard完全兼容，
（1）添加了中文输入方式，默认直接采用维特比算法推荐的使用频率高的几个词，通过参数suggess控制
（2）增加回调函数，在setTag（special_NUM）,之后InstallCallBackFuns(special_NUM,special_function)
    之后，在键盘上点击OK后会自动调用 special_function、
    special_function函数有三个输入参数，分别为输出的文字text,按键优先级 KeyShow_PRO,标签Tag

（3） 例子在最下方
"""
from  KeyBoardForm import Ui_Dialog
from PyQt5 import QtCore, QtGui, QtWidgets
import  sys
from Five.Fothers.FPinyin2Hanzi.createWordsDict import PinYin2Hanzi
import os.path as path
current_path=path.dirname(path.abspath(__file__))+"/forms/icons/"
class KeyBoard(QtWidgets.QDialog):
    SignalALLmessage=QtCore.pyqtSignal(str,int,int)
    #键盘信息，键盘信息属性（0：无，1：只有数字，  2：只有字母 3:混合），标签（默认为0）
    SignalSinglemessage=QtCore.pyqtSignal(str,int)
    SignalChangePinyiin=QtCore.pyqtSignal()
    SignalGetPinyiin = QtCore.pyqtSignal()
    def __init__(self,parent=None,suggess=False):
        super(KeyBoard,self).__init__(parent)
        self.Ui=Ui_Dialog()
        self.Ui.setupUi(self)
        self.Ui.beforeone.setPixmap(QtGui.QPixmap(path.join(current_path,'leftarrow.png')))
        self.Ui.nextone.setPixmap(QtGui.QPixmap(path.join(current_path,'rightarrow.png')))
        self.setWindowTitle("F键盘")
        self.setModal(True)
        self.KeysListNum=[i for i in "0123456789.-"]
        # self.KeysListNum.append(".")
        self.KeysListWord=[i for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
        self.KeysListAbility=["OK","DEL"]
        self.KeyShow_PRO=0#当前LineEdit中的属性 0：无，1：只有数字，  2：只有字母 3:混合
        self.Tag=0#用于标识是哪一个键盘发出的信号
        self.shift=False#小写，True为大写
        self.Chinese=True#中文
        self.querry= PinYin2Hanzi(backen=suggess)
        self.waitReadlist = []
        self.parameter=0
        self.attachInfo=None
        self.CallBackFunlist = dict()
        self.WhichLineEdit=self.Ui.PU_pinyin.objectName()
        self.bindingAllButtons()
        self.InstallLablesEventFilter()
        self.CallBackFunlist.setdefault(0, self.Nonefunc)

    def Nonefunc(self,text,priority,tag,attach):
        pass


    def InstallCallBackFuns(self,tags,func):
        self.CallBackFunlist.setdefault(tags,func)

    def CallBackfunc(self,text,priority,tag,attach):
        if self.CallBackFunlist.get(self.Tag,None) ==None:
            self.Tag=0
        self.CallBackFunlist.get(self.Tag,None)(text,priority,tag,attach)
        self.attachInfo=None


    def clearLineEdit(self):
        self.Ui.K_SHOW.clear()

    def clearAllNotTag(self):
        self.clearLineEdit()
        self.KeyShow_PRO = 0

    def resetALL(self):
        self.KeyShow_PRO = 0
        self.Tag = 0

    def setTag(self,tag):
        self.Tag=tag

    def setattachInfo(self,attach):
        self.attachInfo=attach

    def show(self):
        self.Ui.PU_pinyin.clear()
        self.Ui.K_SHOW.clear()
        super(KeyBoard,self).show()

    def bindingAllButtons(self):
        self.Ui.K_0.clicked.connect(self.KeySender)
        self.Ui.K_1.clicked.connect(self.KeySender)
        self.Ui.K_2.clicked.connect(self.KeySender)
        self.Ui.K_3.clicked.connect(self.KeySender)
        self.Ui.K_4.clicked.connect(self.KeySender)
        self.Ui.K_5.clicked.connect(self.KeySender)
        self.Ui.K_6.clicked.connect(self.KeySender)
        self.Ui.K_7.clicked.connect(self.KeySender)
        self.Ui.K_8.clicked.connect(self.KeySender)
        self.Ui.K_9.clicked.connect(self.KeySender)
        self.Ui.K_A.clicked.connect(self.KeySender)
        self.Ui.K_B.clicked.connect(self.KeySender)
        self.Ui.K_C.clicked.connect(self.KeySender)
        self.Ui.K_D.clicked.connect(self.KeySender)
        self.Ui.K_E.clicked.connect(self.KeySender)
        self.Ui.K_F.clicked.connect(self.KeySender)
        self.Ui.K_G.clicked.connect(self.KeySender)
        self.Ui.K_H.clicked.connect(self.KeySender)
        self.Ui.K_I.clicked.connect(self.KeySender)
        self.Ui.K_J.clicked.connect(self.KeySender)
        self.Ui.K_K.clicked.connect(self.KeySender)
        self.Ui.K_L.clicked.connect(self.KeySender)
        self.Ui.K_M.clicked.connect(self.KeySender)
        self.Ui.K_N.clicked.connect(self.KeySender)
        self.Ui.K_O.clicked.connect(self.KeySender)
        self.Ui.K_P.clicked.connect(self.KeySender)
        self.Ui.K_Q.clicked.connect(self.KeySender)
        self.Ui.K_R.clicked.connect(self.KeySender)
        self.Ui.K_S.clicked.connect(self.KeySender)
        self.Ui.K_T.clicked.connect(self.KeySender)
        self.Ui.K_U.clicked.connect(self.KeySender)
        self.Ui.K_V.clicked.connect(self.KeySender)
        self.Ui.K_W.clicked.connect(self.KeySender)
        self.Ui.K_X.clicked.connect(self.KeySender)
        self.Ui.K_Y.clicked.connect(self.KeySender)
        self.Ui.K_Z.clicked.connect(self.KeySender)
        self.Ui.K_MINUS.clicked.connect(self.KeySender)
        self.Ui.K_DOT.clicked.connect(self.KeySender)
        self.Ui.K_DEL.clicked.connect(self.DEL_clicked)
        self.Ui.K_OK.clicked.connect(self.OK_clicked)
        self.Ui.K_Shift.clicked.connect(self.Shift_clicked)
        self.Ui.PU_Chinese.clicked.connect(self.Chinese_clicked)
        self.SignalChangePinyiin.connect(self.ShowQuerryAnswer)
        self.SignalGetPinyiin.connect(self.GetQuerryAnswer)

    def Chinese_clicked(self):
        self.Chinese = not self.Chinese
        if self.Chinese:
            self.Ui.PU_Chinese.setStyleSheet("background-color: rgb(255, 255, 127);")
            self.Ui.PU_Chinese.setText("中")
        else:
            self.Ui.PU_Chinese.setStyleSheet("background-color: rgb(255, 255, 0);")
            self.Ui.PU_Chinese.setText("英")


    def Shift_clicked(self):
        self.shift= not self.shift
        if self.shift :
            self.Ui.K_Shift.setStyleSheet("background-color: rgb(255, 255, 0);")
            self.Ui.K_Shift.setText("SHIFT")
        else:
            self.Ui.K_Shift.setStyleSheet("background-color: rgb(255, 255, 127);")
            self.Ui.K_Shift.setText("shift")

    def OK_clicked(self):
        text=self.Ui.K_SHOW.text()
        self.SignalALLmessage.emit(text,self.KeyShow_PRO,self.Tag)
        self.CallBackfunc(text,self.KeyShow_PRO,self.Tag,self.attachInfo)
        self.accept()

    def DEL_clicked(self):
        # if self.Chinese:
            if self.WhichLineEdit ==self.Ui.PU_pinyin.objectName():
                self.Ui.PU_pinyin.backspace()
                self.SignalGetPinyiin.emit()
            else:
                self.Ui.K_SHOW.backspace()
        # else:
        #     self.Ui.K_SHOW.backspace()


    def KeySender(self):
        sender=self.sender()
        t = sender.text()

        if t in self.KeysListNum:
                # print "test", t,type(t)
            # if not self.Chinese :
                self.KeyShow_PRO = 1 if self.KeyShow_PRO == 0 or self.KeyShow_PRO == 1 else 3
                # if self.shift==False:
                self.Ui.K_SHOW.insert(t)
                self.SignalSinglemessage.emit(t,1)

        else:
            # print"there",t,type(t)
            if not self.Chinese:
                if t in self.KeysListWord:
                    self.KeyShow_PRO = 2 if self.KeyShow_PRO == 0 or self.KeyShow_PRO == 2 else 3
                    t = ( t if self.shift else t.lower())
                    self.Ui.K_SHOW.insert(t)
                    self.SignalSinglemessage.emit(t,2)
            else:
                self.KeyShow_PRO=3
                self.Ui.PU_pinyin.insert(t.lower())
                self.parameter=0
                self.SignalGetPinyiin.emit()

    def GetQuerryAnswer(self):
        self.waitReadlist = self.querry.GetWords(self.Ui.PU_pinyin.text())
        self.SignalChangePinyiin.emit()

    def ShowQuerryAnswer(self):
        if len(self.waitReadlist)==0 :
            for i in range(7):
                self.Labellist[i + 2].setText('')
        for i in range(7):
            j=self.parameter*7+i
            if j<len(self.waitReadlist):
                self.Labellist[i+2].setText(self.waitReadlist[j])
            else:
                self.Labellist[i + 2].setText('')


    def InstallLablesEventFilter(self):
        self.Ui.K_SHOW.installEventFilter(self)
        self.Ui.PU_pinyin.installEventFilter(self)
        self.Labellist=[self.Ui.nextone,self.Ui.beforeone,
                        self.Ui.HouXuan1_2,self.Ui.HouXuan1_3,self.Ui.HouXuan1_4,
                        self.Ui.HouXuan1_5,self.Ui.HouXuan1_6,self.Ui.HouXuan1_7,
                        self.Ui.HouXuan1_8]
        self.LabellistName=dict()
        index=-2
        for i in self.Labellist:
            i.installEventFilter(self)
            self.LabellistName.setdefault(i.objectName(),index)
            index += 1

    def eventFilter(self, QObject, QEvent):
        if self.LabellistName.get(QObject.objectName(),None)is not None:
            if QEvent.type()==QtCore.QEvent.MouseButtonPress:
                # print len(self.waitReadlist)
                if QObject is self.Ui.nextone and self.parameter >= 0 and self.parameter<(len(self.waitReadlist)//7):
                    self.parameter += 1
                    # print "parameter next",self.parameter
                    self.SignalChangePinyiin.emit()
                elif QObject is self.Ui.beforeone and self.parameter >= 1 :
                        self.parameter -= 1
                        # print "parameter before", self.parameter
                        self.SignalChangePinyiin.emit()
                else:
                    if self.LabellistName.get(QObject.objectName(),None)+7*self.parameter < len(self.waitReadlist):
                        try:
                            self.Ui.K_SHOW.insert(self.waitReadlist[self.LabellistName.get(QObject.objectName(),None)+7*self.parameter])
                        except:
                            pass
                        self.Ui.PU_pinyin.clear()
                return True
            else:
                return  False
        else:
            if QEvent.type() == QtCore.QEvent.MouseButtonPress:
                if QObject.objectName() == self.Ui.PU_pinyin.objectName() :
                    self.WhichLineEdit = QObject.objectName()
                    # print self.WhichLineEdit
                if QObject.objectName() == self.Ui.K_SHOW.objectName():
                    self.WhichLineEdit = QObject.objectName()
                    # print self.WhichLineEdit
            return super(KeyBoard,self).eventFilter(QObject,QEvent)









if __name__ =="__main__":
    def hah(text,priority,tags,attach):
        print "hah"
        print text,priority,tags,attach

    def hah2(text,priority,tags,attach):
        print "haha2"
        print text,priority,tags,attach

    app=QtWidgets.QApplication(sys.argv)
    InstanceMain=KeyBoard()
    InstanceMain.show()
    InstanceMain.setTag(120)
    InstanceMain.setattachInfo("extra infor")
    InstanceMain.InstallCallBackFuns(110,hah)
    InstanceMain.InstallCallBackFuns(120,hah2)
    sys.exit(app.exec_())
    # KeysListNum = [i for i in "0123456789"]
    # print KeysListNum