#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import traceback
from sys import version_info



class FiveLogbasic(object):
    def __init__(self,username='defaultUser',logFilePath='./defaultUserLog.log',filemode='a'):
        self.user=username
        self.logger=logging.getLogger(self.user)
        self.logger.setLevel(logging.DEBUG)
        self.logFileName=logFilePath
        formatter=logging.Formatter('%(asctime)s     %(levelname)s %(message)s ')

        logHand=logging.FileHandler(self.logFileName,filemode)
        logHand.setFormatter(formatter)
        logHand.setLevel(logging.INFO)

        logHandstr=logging.StreamHandler()
        logHandstr.setFormatter(formatter)
        logHandstr.setLevel(logging.ERROR)

        self.logger.addHandler(logHand)
        self.logger.addHandler(logHandstr)


    def debug(self,msg,*args,**kwargs):
        if kwargs.get("lineinfo",False) ==True:
            msg=msg+"\n\t\tLineInfo{}".format(get_filename_function_line())
            del kwargs["lineinfo"]
        self.logger.debug(msg,*args,**kwargs)

    def error(self,msg,*args,**kwargs):
        if kwargs.get("lineinfo",False) ==True:
            msg=msg+"\n\t\tLineInfo{}".format(get_filename_function_line())
            del kwargs["lineinfo"]
        self.logger.error(msg,*args,**kwargs)

    def info(self,msg,*args,**kwargs):
        if kwargs.get("lineinfo",False) ==True:
            msg=msg+"\n\t\tLineInfo{}".format(get_filename_function_line())
            del kwargs["lineinfo"]
        self.logger.info(msg,*args,**kwargs)

    def critical(self,msg,*args,**kwargs):
        if kwargs.get("lineinfo",False) ==True:
            msg=msg+"\n\t\tLineInfo{}".format(get_filename_function_line())
            del kwargs["lineinfo"]
        self.logger.critical(msg,*args,**kwargs)

    def warn(self,msg,*args,**kwargs):
        if kwargs.get("lineinfo",False) ==True:
            msg=msg+"\n\t\tLineInfo{}".format(get_filename_function_line())
            del kwargs["lineinfo"]
        if version_info[0] == 2:
            self.logger.warn(msg,*args,**kwargs)
        else:
            self.logger.warning(msg, *args, **kwargs)


def stacktuplefunctionlinefilename(stackTuple):
    ''' stackTuple: （文件名，行号，函数名，这一行的代码）
    '''
    filename = stackTuple[0]
    linenumber = stackTuple[1]
    funcname = stackTuple[2]
    return  'file:%s,\t func:%s,\t line:%d'%(filename,funcname, linenumber)


def get_filename_function_line(limit=2):  # limit = 1 表示抽取该函数调用者的位置，注意输入到extract_stack中的limit=limit+1
    stackTuple = traceback.extract_stack(limit=limit + 1)[0]
    return stacktuplefunctionlinefilename(stackTuple)




if __name__=="__main__":
    log=FiveLogbasic()
    log.warn("警告")
    log.info("info")
    log.error("错误")
    log.critical("critical")
    log.debug("bug")
    log.debug("bugs",lineinfo=True)
    log.error("致命错误",lineinfo=True)




