#!/usr/bin/env python
# -*- coding: utf-8 -*-
#虚拟SPIDEV的
from  numpy import  sin
from configs import printf
class SPI:
    def __init__(self):
        self.max_speed_hz =0
        self.mode = 0
        self.bits_per_word =0

    def open(self,bus,device):
        printf("打开SPI：{} :{}".format(bus,device))

    def  xfer2(self,data):
        printf("发送:"+"*"*10)
        printf( "".join([hex(i) for i in data]))
        tempdata=[50,60]
        return tuple(tempdata)

    def close(self):
        printf("关闭SPI")


def SpiDev():
    printf("创建示例SPI")
    return SPI()