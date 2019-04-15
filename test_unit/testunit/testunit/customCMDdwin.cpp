#include "stdio.h"
#include "customCMDdwin.h"

struct Screenpara ScreenPara = { 9.8065,0.1,0.1,0.1,0.1 };
struct Screenoutcome ScreenOutCome = { 0,0,0,0 };

/*直接切换到第几个页面*/

void ChangeScreenPage(u16 NumOfPage)
{
	u8 cmd[10] = { 0x5A,0xA5,0x07,0x82,0x00,0x84,0x5A,0x01,0x00,0x00 };
	cmd[8] = (u8)((NumOfPage & 0xff00) >> 8);
	cmd[9] = (u8)(NumOfPage & 0x00ff);
	uart1SendChars(cmd, 10);
}


/*data variable 变量赋值，屏幕采用长整型，4字节,4位小数*/
void uartsend_CMD_DataDisplay(u16 address, u16 highV, u16 lowV)
{
	u8 cmd[10] = { 0x5A,0xA5,0x07,0x82,0x20,0x00,0x00,0x00,0x00,0x00 };
	cmd[4] = (u8)((address & 0xff00) >> 8);
	cmd[5] = (u8)(address & 0x00ff);
	cmd[6] = (u8)((highV & 0xff00) >> 8);
	cmd[7] = (u8)(highV & 0x00ff);
	cmd[8] = (u8)((lowV & 0xff00) >> 8);
	cmd[9] = (u8)(lowV & 0x00ff);
	uart1SendChars(cmd, 10);
}

/*data variable 变量赋值，输入为一个Union 结构的char数组地址，屏幕采用长整型，4字节,4位小数*/
void ChangeScreenVariable(u16 address, char *union_array)
{
	u8 cmd[10] = { 0x5A,0xA5,0x07,0x82,0x20,0x00,0x00,0x00,0x00,0x00 };
	cmd[4] = (u8)((address & 0xff00) >> 8);
	cmd[5] = (u8)(address & 0x00ff);
	cmd[6] = (u8)(union_array[3]);
	cmd[7] = (u8)(union_array[2]);
	cmd[8] = (u8)(union_array[1]);
	cmd[9] = (u8)(union_array[0]);
	uart1SendChars(cmd, 10);
}




//2E是小数点,2D是负号

void checkCMD(u8 length, u8 * rec)
{
	u16 address = 0x0000;
	float value = 0;
	u8 num = 0;
	u8 i = 0, dot = 0, minus = 0;
	if ((length >= 6) && (rec[0] == 0x83) && (rec[4] == 0x5A))//判定是命令是否为text返回的数据
	{
		address = ((rec[1] << 8) & 0xff00)+(rec[2] & 0x00ff) + 0x0001;//地址加一
		
		num = rec[5];//获取text数据有效位数
					 //解析text数据为float型
		for (i = 0; i<num; i++)
		{
			if ((rec[i + 6] >= 0x30)&(rec[i + 6] <= 0x39))//判断是数值
			{

				value = value * 10 + (rec[i + 6] - 0x30);
				if (dot != 0x00)//计算小数部分的位数
				{
					dot += 1;
				}
			}
			else
			{
				if (rec[i + 6] == 0x2E)
				{
					dot = 0x01;//出现小数点
				}
				if (rec[i + 6] == 0x2D)
				{
					minus = 0x01;//出现负号
				}
			}
		}

		if (dot != 0x00)//获取小数部分
		{
			for (i = 1; i < dot; i++)
			{
				value /= 10;
			}
		}
		if (minus == 0x01)//获得正负号
		{
			value = -1 * value;
		}

		//判断text数据地址来给参数赋值
		//printf("------------------:%f\n", value);
		switch (address)
		{
		case (u16)(ADDR_XI_SHU_K) : ScreenPara.s_XiShu_K = value; break;
		case (u16)(ADDR_RONG_QI_YA_LI_Pr) : ScreenPara.s_RongQiYaLi_Pr = value; break;
		case (u16)(ADDR_FA_BAN_MIAN_JI_A) : ScreenPara.s_FaBanMianJi_A = value; break;
		case (u16)(ADDR_ZHENG_DING_YA_LI_Pset2) : ScreenPara.s_ZhengDingYaLi_Pset2 = value; break;
		case (u16)(ADDR_TAN_HUANG_ZEN_LIANG_Q) : ScreenPara.s_TanHuangZenLiang_Q = value; break;

		}

	}

}




//计算提升力并返回，并会把提升力保存在ScreenOutCome.s_out_TiShengLi_F
//由公式F(kg)=（Pset2(MPa)-Pr(MPa)*A(mm^2)）/(系数k9.8066)
float  calculate_TiShengLi_F(void)
{
	float value = 0;
	value = ((ScreenPara.s_ZhengDingYaLi_Pset2 - ScreenPara.s_RongQiYaLi_Pr)*ScreenPara.s_FaBanMianJi_A);
	value /= ScreenPara.s_XiShu_K;
	ScreenOutCome.s_out_TiShengLi_F = value;
	return value;

}

//计算整定压力Pset1并返回，保存在ScreenOutCome.s_out_ZhengDingYaLi_Pset1
//由公式Pset1=Pr+((F峰值*9.8065)/A)
float calculate_ZhengDingYaLi_Pset1(void)
{
	float value = 0;
	value = ScreenPara.s_RongQiYaLi_Pr + ((ScreenOutCome.s_out_FengZhi_F*ScreenPara.s_XiShu_K) / ScreenPara.s_FaBanMianJi_A);
	ScreenOutCome.s_out_ZhengDingYaLi_Pset1 = value;
	return value;
}



//计算调整量L并返回，保存在ScreenOutCome.s_out_TiaoZhengLiang_L
float calculate_TiaoZhengLiang_L(void)
{
	float value;
	value = (ScreenPara.s_ZhengDingYaLi_Pset2 - ScreenOutCome.s_out_ZhengDingYaLi_Pset1) / ScreenPara.s_TanHuangZenLiang_Q;
	ScreenOutCome.s_out_TiaoZhengLiang_L = value;
	return value;
}

