#pragma once

#ifndef __CUS_CMD_DWIN__H__
#define __CUS_CMD_DWIN__H__

//#include "common.h" 
//#include "usart1.h"
#include "unittest.h"
//屏幕整形数据与单片机数据类型转换，不考虑正负号
#define SCREEN_FLOAT2U32(value)    ((u32)((value)*10000))  //更改float类型为u32，
#define  SCREEN_U32TOFLOAT(value)   (((float)(value))/10000) //更改u32类型为float

//屏幕输入参数地址
#define ADDR_XI_SHU_K                               0x4000 //系数k的地址
#define ADDR_RONG_QI_YA_LI_Pr                       0x4020  //容器压力的地址
#define ADDR_FA_BAN_MIAN_JI_A                       0x4040  //阀瓣面积的地址
#define ADDR_ZHENG_DING_YA_LI_Pset2                 0x4060  //整定压力的地址
#define ADDR_TAN_HUANG_ZEN_LIANG_Q                  0x4080  //弹簧增量的地址

//屏幕上计算结果的地址
#define ADDR_TiShengLi_F                            0x40a0//提升力F
#define ADDR_ZhengDingYaLi_Pset1                    0x40c0//整定压力Pset1
#define ADDR_TiaoZhengLiang_L                       0x40e0//调整量L                      
#define ADDR_FengZhi_F                              0x4110//峰值

struct Screenpara  //屏幕输入参数
{
	float s_XiShu_K;
	float s_RongQiYaLi_Pr;
	float s_FaBanMianJi_A;
	float s_ZhengDingYaLi_Pset2;
	float s_TanHuangZenLiang_Q;
};



struct Screenoutcome//计算结果
{
	float s_out_TiShengLi_F;//由公式F(kg)=（Pset2(MPa)-Pr(MPa)*A(mm^2)）/(系数k9.8066)
	float s_out_FengZhi_F;//由AD输入曲线的峰值点。
	float s_out_ZhengDingYaLi_Pset1;//由公式Pset1=Pr+((F峰值*9.8065)/A)
	float s_out_TiaoZhengLiang_L;//(Pset2-Pset1)/Q安全弹簧增量
};

union Screen_uint32//发送数据时用的共用体
{
	u32 s_uint32;
	char s_char[4];
};

/*functions*/
void ChangeScreenPage(u16 NumOfPage);//改变屏幕上的页数
void ChangeScreenVariable(u16 address, char *union_array);//改变屏幕上变量的值，(地址，值)
void checkCMD(u8 length, u8 * rec);//解析屏幕串口返回的命令，并给相应ScreenPara赋值
void uartsend_CMD_DataDisplay(u16 address, u16 highV, u16 lowV);

float  calculate_TiShengLi_F(void);//计算提升力
float calculate_ZhengDingYaLi_Pset1(void);//计算整定压力Pset1
float calculate_TiaoZhengLiang_L(void);//计算调整量L



#endif

