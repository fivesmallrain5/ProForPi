#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

level0= False
level1=False


def stacktuplefunctionlinefilename(stackTuple):
    ''' stackTuple: （文件名，行号，函数名，这一行的代码）
    '''
    filename = stackTuple[0]
    linenumber = stackTuple[1]
    funcname = stackTuple[2]
    return  'file:%s,\t func:%s,\t line:%d'%(filename,funcname, linenumber)


def get_filename_function_line(limit=1):  # limit = 1 表示抽取该函数调用者的位置，注意输入到extract_stack中的limit=limit+1
    stackTuple = traceback.extract_stack(limit=limit + 1)[0]
    return stacktuplefunctionlinefilename(stackTuple)


def printf(strs,level0=level0,level1=level1):
    if level1:
        print('\t%s' % get_filename_function_line(limit=2))
        # print sys._getframe().f_code.co_filename," : ",sys._getframe().f_lineno
        print strs
    elif level0:
        print('\t%s' % get_filename_function_line(limit=2))
        print strs


# def ReverseCode(lists):
#     """实现补码"""
#     temp = lists[0] & 0x80
#     a = (lists[0] & 0x7f)
#     if temp == 0x80:
#         a = ~a & 0x7f
#         b = (~(lists[1])) & 0xff
#         return -(a*256+b+1)
#     else:
#         return a*256+lists[1]

def ReverseCode(lists):
    """实现补码"""
    lis=[0,0]
    lis[0]=lists[0]
    # print lis[0]
    lis[1]=lists[1]
    # print lis[1]
    temp = lis[0] & 0x40
    a = (lis[0] & 0x3f)
    if temp == 0x40:
        a = ~a & 0x3f
        b = (~(lis[1])) & 0xff
        return -(a*512+b*2+1)
    else:
        return a*512+lis[1]*2


if __name__ =="__main__":
    print ReverseCode((128,0))
    print ReverseCode((255,254))