#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Vspidevtest as spidev#实际使用时注释掉这一行，使用下面一行

#import  spidev
"""
针对我们的树莓派必须使用bus=1,device=0或者1
spi 引脚为(BCM）
MOSI :20        SCLK:21
MISO: 21        CEO和CE1应该是18 ，17（这里不确定,要更改自己查linux源码去，我看不懂）


"""



"""
管脚：
CS-:      只有一个设备时，可以一直为低
DRDY:       数据转换准备好了，低电平准备好 当CS-为高时也可以使用
DIN  :      SCLK下降沿接收数据
DOUT/DRDY- :    SCLK上升沿传送数据 CS-为高时高阻抗，多设备使用时最好不用第二功能          
DRDY-:      一旦为低电平就可以读取数据了，下降沿开始读数据？
"""

#----------------------------------------#
#命令

CmdRESET=0b00000110
CmdSTART_SYNC=0b00001000
CmdPOWERDOWN=0b00000010
CmdRDATA=0b00010000

CmdR_REG=0b00100000 #  |0brrnn  读寄存器地址rr后面nn+1字节数据
CmdW_REG=0b01000000 #  |0brrnn  写寄存器地址rr后面nn+1字节数据
# REG_0=0b0100 #example  R_REG|REG_1|0b10 读寄存器REG_1后面三个字节

#----------------------------------------#
#----------------------------------------#
#参数

#----------------------------------------#

#----------------------------------------#
#硬件参数设置
#----------------------------------------#
#channel:
Channel_0,Channel_1,Channel_2,Channel_3=0,1,2,3
#增益：
Gain_1, Gain_2, Gain_4, Gain_8,  Gain_16,  Gain_32,  Gain_64,  Gain_128=\
0b000,  0b001,  0b010,  0b011,   0b100,    0b101,    0b110,    0b111






# ADS1120 初始化基本信息
BITS = 8
SPEED = 1000
DELAY = 01
MODE = 0b01  #[CPOL|CPHA]


class ADS1120:
    def __init__(self, bus=1, device=0):
        """ADSii20初始化"""
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = SPEED
        self.spi.mode = MODE
        self.spi.bits_per_word = 8
        self.reset()



    def reset(self):
        self.spi.xfer2([CmdRESET])

    def Close(self):
        self.spi.close()

    def PowerDown(self):
        self.spi.xfer2([CmdPOWERDOWN])

    def GetAD(self ,channel,NumOfBytes=2):
        """默认从每个channel获取2个字节数"""
        self.ConfigAD(channel)
        self.spi.xfer2([CmdSTART_SYNC])#对应ADStartConversion()
        tempdata=[0x00 for i in range(NumOfBytes)]
        for i in range(10):
            self.spi.xfer2([0xff])
        realdta=self.ReadData(tempdata)
        # print "fanhui",realdta
        return  tuple(realdta)


    def ConfigAD(self,channel):
        Init_Config_0=[0x81,0x91,0xa1,0xb1]
        # 以下依次为：1K采样；5vAVDD作为参考电压；
        Init_Config_1,Init_Config_2,Init_Config_3=0xc0,0xc0,0x00
        self.WriteRegister(0x00,0x04,
            [Init_Config_0[channel],
             Init_Config_1,Init_Config_2,Init_Config_3])
        # self.spi.xfer2([CmdW_REG|(0<<2&0x0c)|((4-1)&0x03)])
        # self.spi.xfer2([0x91])
        # self.spi.xfer2([0xc0])
        # self.spi.xfer2([0xc0])
        # self.spi.xfer2([0x00])
        #
        # self.spi.xfer2([0xff])
        for i in range(10):
            self.spi.xfer2([0xff])
        # print  "four register：",self.ReadRegister(NeedReturn=True)



    def WriteRegister(self,StartAddress, NumRegs, Datas):
        #Datas 必须为列表
        assert isinstance(Datas, list)
        assert len(Datas)==NumRegs
        self.spi.xfer2([CmdW_REG|(StartAddress<<2&0x0c)|((NumRegs-1)&0x03)])
        # time.sleep(0.1)
        self.spi.xfer2(Datas)
        # time.sleep(0.1)

    def ReadRegister(self,StartAddress=0x0, NumRegs=4,NeedReturn=None):
        # 默认读取0寄存器后四个字节,如果需要返回寄存器的数据，将NeedReturn改为True
        self.spi.xfer2([CmdR_REG|(StartAddress<<2&0x0c)|((NumRegs-1)&0x03)])
        if NeedReturn==None:
            for i in range(NumRegs):
                self.spi.xfer2([0xff])
                # time.sleep(0.1)
        else:
            temp=[]
            for i in range(NumRegs):
                temp.append(self.spi.xfer2([0xff])[0])
                # time.sleep(0.1)
            return temp


    def ADStartConversion(self):
        self.spi.xfer2([CmdSTART_SYNC])
        # time.sleep(0.1)

    def ReadData(self,Datas):
        """在GetAD之后，ADStartConversion，sleep,ReadData 同时使用应该效率会高一点
            因为烧了发送配置某一Channel 那部分的数据
        """
        assert isinstance(Datas,list)#保证读取的数据是列表格式
        self.spi.xfer2([CmdRDATA])#先写一个读的命令字
        # time.sleep(0.1)
        datas=self.spi.xfer2(Datas)
        # time.sleep(0.1)
        return  datas


#
#
# if __name__ =="__main__":
#
#     how=50000
#     i=0
#     LookupTable = dict([(x, ReverseCode(x)) for x in [(m, n) for m in range(256) for n in range(256)]])
#     ad1120 = ADS1120(1, 0)
#     with open("/home/pi/spitest.txt","w+") as f:
#          while i <how:
#             i+=1
#             data=ad1120.GetAD(1)
#             line="{}---{}".format(data,LookupTable.get(data,111))
#             f.writelines(line)
#             if i==1000:
#                 f.flush()
#             t =input("please input something")
#             if int(t)==500:
#                 break
#
#         # time.sleep(0.1)





if __name__ =="__main__":
    pass
    # ad1120=ADS1120(1,0)
    # while 1:
    #     t= raw_input("测试：")
    #     if int(t) == 500:
    #        break
    #     print "AD数据",ad1120.GetAD(1)
    #     # time.sleep(0.1)
    # ad1120.Close()


    # LookupTable = dict([(x, ReverseCode(x)) for x in [(m, n) for m in range(256) for n in range(256)]])
    # print LookupTable[(128,0)]  #-32768
    # spi=spidev.SpiDev()
    # spi = spidev.SpiDev()
    # spi.open(1, 0)
    # spi.max_speed_hz = SPEED
    # spi.mode =0b01
    # spi.bits_per_word = 8
    #
    # spi.xfer([CmdRESET ])
    # while 1:
    #     t= raw_input("测试：")
    #     if int(t) == 500:
    #        break
    #
    #     # print CmdW_REG | (00 << 2 & 0x0c) | ((1 - 1) & 0x03)
    #     print  spi.xfer([CmdW_REG | (00 << 2 & 0x0c) | ((4 - 1) & 0x03)])
    #     print  spi.xfer([0x36,0x57,0x24,0x85])
    #     # print CmdR_REG | (00 << 2 & 0x0c) | ((1 - 1) & 0x03)
    #     print spi.xfer([CmdR_REG | (00 << 2 & 0x0c) | ((4 - 1) & 0x03)])
    #
    #     print ReverseCode(tuple(spi.xfer([0xff,0xff])))
    #     print ReverseCode(tuple(spi.xfer([0xff,0xff])))
    #
    #
    #     print spi.xfer([0xff])
        # print type(spi.xfer2([0xff]))








