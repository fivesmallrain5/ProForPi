#pragma once

#ifndef __CUS_CMD_DWIN__H__
#define __CUS_CMD_DWIN__H__

//#include "common.h" 
//#include "usart1.h"
#include "unittest.h"
//��Ļ���������뵥Ƭ����������ת����������������
#define SCREEN_FLOAT2U32(value)    ((u32)((value)*10000))  //����float����Ϊu32��
#define  SCREEN_U32TOFLOAT(value)   (((float)(value))/10000) //����u32����Ϊfloat

//��Ļ���������ַ
#define ADDR_XI_SHU_K                               0x4000 //ϵ��k�ĵ�ַ
#define ADDR_RONG_QI_YA_LI_Pr                       0x4020  //����ѹ���ĵ�ַ
#define ADDR_FA_BAN_MIAN_JI_A                       0x4040  //��������ĵ�ַ
#define ADDR_ZHENG_DING_YA_LI_Pset2                 0x4060  //����ѹ���ĵ�ַ
#define ADDR_TAN_HUANG_ZEN_LIANG_Q                  0x4080  //���������ĵ�ַ

//��Ļ�ϼ������ĵ�ַ
#define ADDR_TiShengLi_F                            0x40a0//������F
#define ADDR_ZhengDingYaLi_Pset1                    0x40c0//����ѹ��Pset1
#define ADDR_TiaoZhengLiang_L                       0x40e0//������L                      
#define ADDR_FengZhi_F                              0x4110//��ֵ

struct Screenpara  //��Ļ�������
{
	float s_XiShu_K;
	float s_RongQiYaLi_Pr;
	float s_FaBanMianJi_A;
	float s_ZhengDingYaLi_Pset2;
	float s_TanHuangZenLiang_Q;
};



struct Screenoutcome//������
{
	float s_out_TiShengLi_F;//�ɹ�ʽF(kg)=��Pset2(MPa)-Pr(MPa)*A(mm^2)��/(ϵ��k9.8066)
	float s_out_FengZhi_F;//��AD�������ߵķ�ֵ�㡣
	float s_out_ZhengDingYaLi_Pset1;//�ɹ�ʽPset1=Pr+((F��ֵ*9.8065)/A)
	float s_out_TiaoZhengLiang_L;//(Pset2-Pset1)/Q��ȫ��������
};

union Screen_uint32//��������ʱ�õĹ�����
{
	u32 s_uint32;
	char s_char[4];
};

/*functions*/
void ChangeScreenPage(u16 NumOfPage);//�ı���Ļ�ϵ�ҳ��
void ChangeScreenVariable(u16 address, char *union_array);//�ı���Ļ�ϱ�����ֵ��(��ַ��ֵ)
void checkCMD(u8 length, u8 * rec);//������Ļ���ڷ��ص����������ӦScreenPara��ֵ
void uartsend_CMD_DataDisplay(u16 address, u16 highV, u16 lowV);

float  calculate_TiShengLi_F(void);//����������
float calculate_ZhengDingYaLi_Pset1(void);//��������ѹ��Pset1
float calculate_TiaoZhengLiang_L(void);//���������L



#endif

