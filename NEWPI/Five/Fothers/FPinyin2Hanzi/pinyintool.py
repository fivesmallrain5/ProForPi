#!/usr/bin/env python
# -*- coding: utf-8 -*-

import  util
from util import __pinyin as pinyindags
def ReshapePinyin(pinyin):
    temppinyin = ''
    pinyin=pinyin.lower()
    for i in pinyin:  # 去掉一个音节重复的部分
        if i not in temppinyin:
            temppinyin += i
    pinyin = temppinyin

    if pinyin in util.__pinyin:
        return  pinyin
    else:
        yinjieList=[]
        while len(pinyin)!=0:
            pinyin,unit=getOneUnit(pinyin)
            yinjieList.append(unit)
        while len(yinjieList)!=0:
            pinyin=getyinjie(yinjieList)
            if pinyin in util.__pinyin:
                return pinyin
            else:
                yinjieList.pop()
        return  None
        # raise  Exception("{} can't reshape to a tone,it may be a single shengmu".format(pinyin))




def getyinjie(yinjielist):
    yinjie=''
    for data in yinjielist:
        yinjie+=data
    return  yinjie


def getOneUnit(pinyin):
    unit=''
    tempshenshenmu = util.get_shengmu(pinyin)
    if tempshenshenmu is not None:
        unit=tempshenshenmu
        pinyin = pinyin[len(tempshenshenmu):]
    else:
        tempyumu = util.get_yunmu(pinyin)
        if tempyumu is not None:
            unit =tempyumu
            pinyin = pinyin[len(tempyumu):]
        else:
            pinyin=''
    return  pinyin, unit



def ReshapePinyin2(pinyin):
    if pinyin in pinyindags:
        return pinyin
    else:
        return None