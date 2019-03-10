#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import  QtCore,QtWidgets,QtGui
from  forms.loginForm import  Ui_Dialog
from Five.Fothers import  FiveFileParser
from Five.Fpyqtwidget import  KeyBoard

path = 'loginsetting.txt'
class loginOBJ(QtWidgets.QDialog):
    Signal_infor=QtCore.pyqtSignal(str,str)
    Signal_Finish=QtCore.pyqtSignal(bool)

    def __init__(self,parent=None,logintablePath=None,Keyboard=None):
        super(loginOBJ,self).__init__(parent)
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle('登录')
        self.ui.LOGIN_PB_OK.clicked.connect(self.slotPushbuttonOK)
        self.ui.LOGIN_PB_NEW.clicked.connect(self.slotPushbuttonNew)
        self.logintablePath=logintablePath
        self.Keyboard=Keyboard
        self.regions=[]
        self.getRegions()

        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)

        self.New = QtWidgets.QDialog()
        self.New.setFont(font)
        self.New.resize(300, 200)
        self.New.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.New.setWindowTitle('新建')
        self.New.setModal(True)
        layout = QtWidgets.QVBoxLayout(self.New)
        layout1 = QtWidgets.QHBoxLayout()
        self.la_region = QtWidgets.QLabel(self.New)
        self.la_region.setText('地区')
        self.la_region.setFont(font)
        self.co_region = QtWidgets.QComboBox(self.New)
        self.co_region.setMinimumSize(100, 23)
        layout1.addWidget(self.la_region)
        layout1.addWidget(self.co_region)
        for i in range(len(self.regions)):
            self.co_region.addItem(self.regions[i][0])

        layout2 = QtWidgets.QHBoxLayout()
        self.la_gen = QtWidgets.QLabel(self.New)
        self.la_gen.setText("电厂")
        self.la_gen.setFont(font)
        self.line_edit = QtWidgets.QLineEdit(self.New)
        self.line_edit.setMinimumSize(100, 23)


        layout2.addWidget(self.la_gen)
        layout2.addWidget(self.line_edit)

        self.pushok = QtWidgets.QPushButton(self.New)
        self.pushok.setText("确定")
        self.pushignore = QtWidgets.QPushButton(self)
        self.pushignore.setText("取消")
        layout3 = QtWidgets.QHBoxLayout()
        layout3.addWidget(self.pushok)
        layout3.addWidget(self.pushignore)

        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addLayout(layout3)
        self.pushok.clicked.connect(self.slotNewPushOk)
        self.pushignore.clicked.connect(self.New.accept)
        if self.Keyboard != None:
            self.Keyboard.setTag(1)
            self.Keyboard.InstallCallBackFuns(1,self.test)


    def getRegions(self):
        path=self.logintablePath
        regioninfor=FiveFileParser.readTable(path)
        if regioninfor !=None:
            for _,item in regioninfor.iteritems():
                regions=item['cellContent']
                for keys,values in regions.iteritems():
                    self.regions.append([keys,values])
                break
            self.ui.LOGIN_region.currentIndexChanged.connect(self.activeComboxGen)
            self.activeComboxRegin()

    def activeComboxRegin(self):
        self.ui.LOGIN_region.clear()
        for i in range(len(self.regions)):
            self.ui.LOGIN_region.addItem(self.regions[i][0])


    def activeComboxGen(self,i):
        self.ui.LOGIN_gen.clear()
        if len(self.regions)!=0 :
            temp=self.regions[i][1].strip().split('.')
            for j in range(len(temp)):
                if temp[j]=='':
                    continue
                self.ui.LOGIN_gen.addItem(temp[j])
        else:
            pass

    def slotPushbuttonOK(self):
        if self.ui.LOGIN_region.currentText() !='' and self.ui.LOGIN_gen.currentText() !='':
            self.Signal_infor.emit(self.ui.LOGIN_region.currentText(),self.ui.LOGIN_gen.currentText())
            self.Signal_Finish.emit(True)
            self.accept()
        else:
            self.Signal_Finish.emit(False)


    def slotPushbuttonNew(self):
        self.New.show()
        self.line_edit.installEventFilter(self)
        self.New.exec_()

#----------------------------------NEW---------------
    def slotNewPushOk(self):
        path=self.logintablePath
        if self.line_edit.text()!="":
            temp=self.regions[self.co_region.currentIndex()][1]
            temp="".join([temp,".",self.line_edit.text()])
            self.regions[self.co_region.currentIndex()][1]=temp
        # print self.regions[self.co_region.currentIndex()][1]
        self.activeComboxRegin()
        self.ui.LOGIN_region.setCurrentIndex(self.co_region.currentIndex())
        self.ui.LOGIN_gen.setCurrentIndex(
            len(self.regions[self.co_region.currentIndex()][1].strip().split('.'))-1)
        table=dict()
        for i in self.regions:
            table.setdefault(i[0],i[1])
        FiveFileParser.updataTable(table,"regions",path)
        del table
        self.New.accept()

    def Slot_Fnish_Region(self):
        self.hide()
        self.deleteLater()


    def eventFilter(self, QObject, QEvent):
        if QObject==self.line_edit:
            if QEvent.type()==QtCore.QEvent.MouseButtonPress:
                pass
                if self.Keyboard !=None:
                    self.Keyboard.show()
            return  False
        else:
            return super(loginOBJ, self).eventFilter(QObject, QEvent)

    def test(self,text,priority,tags,attach):
        # print text, priority, tags
        self.line_edit.setText(text)









if __name__ =="__main__":
    import  sys
    app=QtWidgets.QApplication(sys.argv)
    KeyboradInstance=KeyBoard.KeyBoard()
    InstanceMain = loginOBJ(Keyboard=KeyboradInstance)
    InstanceMain.show()
    # path='loginsetting.txt'
    # # FiveFileParser.createTable(path)
    # tables={'黑龙江':'黑1.黑2.黑3.','湖南':'湖1.湖2.湖3.'}
    # FiveFileParser.insertTable(tables,'地区',path,-1)
    # print FiveFileParser.readTable(path)
    sys.exit(app.exec_())

