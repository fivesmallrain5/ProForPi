#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
def join(base,list):
    for data in list:
        base = os.path.join(base, data)
    return base
def make_exclusive_name(dirpath,name,add_suffix='cp'):
    filename = os.listdir(dirpath)
    print filename
    name,end=name.split('.')
    if isinstance(add_suffix,str):
        while ''.join([name,end]) in filename:
            name+='cp'
        return  name+end
    elif callable(add_suffix):
        while ''.join([name,end]) in filename:
            name+=add_suffix()
        return  name+end
    else:
        raise ValueError(add_suffix)

if __name__ =="__main__":
    # print join(os.getcwd(),['a','b'])
    print make_exclusive_name('D:\Projections\NEWPI\TESTdir123456789\usb','test.txt','cp')