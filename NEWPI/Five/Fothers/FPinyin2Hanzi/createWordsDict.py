#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""
author:fivesmallrain



"""


import  sqlite3 as sq
import pickle
from  os import path
from  pinyintool import ReshapePinyin2 as ReshapePinyin

backenFlag=False

current_path=path.dirname(path.abspath(__file__))

class PinYin2Hanzi(object):

    def __init__(self,useWhat='pickle',backen=False):
        global  backenFlag
        self.fileOK =False
        self.useWhat=useWhat
        self.DagsPath=None
        self.database=None
        self.pickle=None
        self.backen=backen
        if self.backen :
            try:
                from Pinyin2Hanzi import DefaultHmmParams
                from Pinyin2Hanzi import viterbi
                self.hmmparams = DefaultHmmParams()
                self.viterbi=viterbi
            except:
                raise  Exception('lost Pinyin2Hanzi package,'
                                 'please find that package ,'
                                 'or set backen=False')
        self.CheckFiles()


    def CreateDagData(self):
        if self.useWhat=='pickle':
            CreatDag2Dict()
        elif self.useWhat =='sql':
            CreateDag2Sqlite3()

    def CheckFiles(self):
        paths=current_path
        if self.useWhat == 'pickle':
            if path.exists(path.join(paths,'PinyinChinesePickle.data')):
                self.fileOK=True
            elif path.exists(path.join(paths,'chinese.txt')):
                self.CreateDagData()
                self.fileOK = True
                self.DagsPath=path.join(paths,'PinyinChinesePickle.data')
            else:
                raise Exception('loss chinese.txt file!')
            with open(path.join(paths,'PinyinChinesePickle.data'),'r') as f:
                self.pickle=pickle.load(f)
        elif self.useWhat =='sql':
            if path.exists(path.join(paths, 'PinyinChineseSQL.data')):
                self.fileOK = True
            elif path.exists(path.join(paths,'chinese.txt')):
                self.CreateDagData()
                self.fileOK = True
                # self.DagsPath = path.join(paths, 'PinyinChineseSQL.data')
            else:
                raise Exception('loss chinese.txt file!')
            self.database = sq.connect(path.join(paths, 'PinyinChineseSQL.data'))

    def GetWords(self,pinyin,num=None):
        pinyin=ReshapePinyin(pinyin)
        if pinyin is None:
            return  []

        if self.fileOK:
            templist=[]
            if self.backen:
                templist = [item.path[0] for item in
                            self.viterbi(hmm_params=self.hmmparams, observations=(pinyin,), path_num=10)]
            if self.useWhat == 'pickle':
                templist.extend(GetWordsfromPickle(pinyin, self.pickle, num))
                return templist
            elif self.useWhat =='sql':
                templist.extend(GetWordsfromSQL(pinyin, self.database, num))
                return templist
        else:
            raise Exception('Check file failed!')

    def Close(self):
        if self.database is not None:
            self.database.close()






def CreatWordList(values):
    k,word,wordlist=0,[],[]
    for i in values:
        word.append(i)
        k+=1
        if k==3:
            word="".join(word)
            wordlist.append(word)
            word=[]
            k=0
    return wordlist

def EncodeWordlist2utf(wordlist):
    teplist=""
    for i in wordlist:
        temp=i.decode('utf-8')
        teplist=teplist+temp
    return  teplist

"""
选择文字的两种方式 sqlite3 pickle
"""

def GetWordsfromSQL(pinyin,database,num=None):
    cursor=database.execute("select bianma from words where pinyin in  ('{}') limit 1".format(pinyin))
    datas = cursor.fetchone()[0]
    temp=[]
    for index,da in enumerate(datas):
        temp.append(da)
        if index+1==num:
            return temp
    return temp

def GetWordsfromPickle(pinyin,dicDags,num=None):
    datas= dicDags[pinyin]
    temp = []
    for index, da in enumerate(datas):
        temp.append(da)
        if index + 1 == num:
            return temp
    return temp


"""
创建dags，两种方式，sqlite3 pickle
"""
def CreateDag2Sqlite3():

    db = sq.connect( path.join(current_path, "PinyinChineseSQL.data"))
    db.execute('create table words (id integer primary key, pinyin text key ,bianma text) ')
    with open(path.join(current_path,"chinese.txt"), "r") as f:
        realindex=0
        for index, line in enumerate(f.readlines()):
            realindex+=1
            # raw_input("input")
            if line=='\n':
                realindex-=1
                continue
            print realindex
            linnes = line.split("=")
            print linnes
            keys, values = linnes[0].strip(), linnes[1].strip()
            temp = EncodeWordlist2utf(CreatWordList(values))
            db.execute('insert into words (id ,pinyin,bianma) values (?,?,?)', (realindex, keys, temp))
            if index/30==0:
                db.commit()
    db.commit()
    db.close()
    print "Create Dag to Sqlite3 Finish!"

def CreatDag2Dict():
    Dags=dict()
    with open(path.join(current_path,"chinese.txt"), "r") as f:
        realindex = 0
        for index, line in enumerate(f.readlines()):
            realindex += 1
            if line == '\n':
                realindex -= 1
                continue
            if line=='\r\n':
                continue
            print realindex
            linnes = line.split("=")
            print linnes
            keys, values = linnes[0].strip(), linnes[1].strip()
            temp = EncodeWordlist2utf(CreatWordList(values))
            Dags.setdefault(keys,temp)
    with open(path.join(current_path,'PinyinChinesePickle.data'),'w') as f:
        pickle.dump(Dags,f)
    print "Create Dag to pickle Finish!"



"""
使用类的例子，两种创建方式(初始化的时候用PinYin2Hanzi('sql')或PinYin2Hanzi())，
建议使用默认的pickle方式，采用字典，速度快
如果相使用sqlite的一些特性可以使用sql

当 backen=True 时，将会使得输出的数字前面的15个很具有推荐性，GetWords(i,7)输出会为7+15个了

如果不想使用类，可以函数的方法


"""
if __name__ =="__main__":
    """
    首次创建数据拼音汉字数据库
    
    """



    B=PinYin2Hanzi('pickle')

    B.Close()










