#include "stdio.h"
#include "customCMDdwin.h"

struct Screenpara ScreenPara = { 9.8065,0.1,0.1,0.1,0.1 };
struct Screenoutcome ScreenOutCome = { 0,0,0,0 };

/*ֱ���л����ڼ���ҳ��*/

void ChangeScreenPage(u16 NumOfPage)
{
	u8 cmd[10] = { 0x5A,0xA5,0x07,0x82,0x00,0x84,0x5A,0x01,0x00,0x00 };
	cmd[8] = (u8)((NumOfPage & 0xff00) >> 8);
	cmd[9] = (u8)(NumOfPage & 0x00ff);
	uart1SendChars(cmd, 10);
}


/*data variable ������ֵ����Ļ���ó����ͣ�4�ֽ�,4λС��*/
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

/*data variable ������ֵ������Ϊһ��Union �ṹ��char�����ַ����Ļ���ó����ͣ�4�ֽ�,4λС��*/
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




//2E��С����,2D�Ǹ���

void checkCMD(u8 length, u8 * rec)
{
	u16 address = 0x0000;
	float value = 0;
	u8 num = 0;
	u8 i = 0, dot = 0, minus = 0;
	if ((length >= 6) && (rec[0] == 0x83) && (rec[4] == 0x5A))//�ж��������Ƿ�Ϊtext���ص�����
	{
		address = ((rec[1] << 8) & 0xff00)+(rec[2] & 0x00ff) + 0x0001;//��ַ��һ
		
		num = rec[5];//��ȡtext������Чλ��
					 //����text����Ϊfloat��
		for (i = 0; i<num; i++)
		{
			if ((rec[i + 6] >= 0x30)&(rec[i + 6] <= 0x39))//�ж�����ֵ
			{

				value = value * 10 + (rec[i + 6] - 0x30);
				if (dot != 0x00)//����С�����ֵ�λ��
				{
					dot += 1;
				}
			}
			else
			{
				if (rec[i + 6] == 0x2E)
				{
					dot = 0x01;//����С����
				}
				if (rec[i + 6] == 0x2D)
				{
					minus = 0x01;//���ָ���
				}
			}
		}

		if (dot != 0x00)//��ȡС������
		{
			for (i = 1; i < dot; i++)
			{
				value /= 10;
			}
		}
		if (minus == 0x01)//���������
		{
			value = -1 * value;
		}

		//�ж�text���ݵ�ַ����������ֵ
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




//���������������أ������������������ScreenOutCome.s_out_TiShengLi_F
//�ɹ�ʽF(kg)=��Pset2(MPa)-Pr(MPa)*A(mm^2)��/(ϵ��k9.8066)
float  calculate_TiShengLi_F(void)
{
	float value = 0;
	value = ((ScreenPara.s_ZhengDingYaLi_Pset2 - ScreenPara.s_RongQiYaLi_Pr)*ScreenPara.s_FaBanMianJi_A);
	value /= ScreenPara.s_XiShu_K;
	ScreenOutCome.s_out_TiShengLi_F = value;
	return value;

}

//��������ѹ��Pset1�����أ�������ScreenOutCome.s_out_ZhengDingYaLi_Pset1
//�ɹ�ʽPset1=Pr+((F��ֵ*9.8065)/A)
float calculate_ZhengDingYaLi_Pset1(void)
{
	float value = 0;
	value = ScreenPara.s_RongQiYaLi_Pr + ((ScreenOutCome.s_out_FengZhi_F*ScreenPara.s_XiShu_K) / ScreenPara.s_FaBanMianJi_A);
	ScreenOutCome.s_out_ZhengDingYaLi_Pset1 = value;
	return value;
}



//���������L�����أ�������ScreenOutCome.s_out_TiaoZhengLiang_L
float calculate_TiaoZhengLiang_L(void)
{
	float value;
	value = (ScreenPara.s_ZhengDingYaLi_Pset2 - ScreenOutCome.s_out_ZhengDingYaLi_Pset1) / ScreenPara.s_TanHuangZenLiang_Q;
	ScreenOutCome.s_out_TiaoZhengLiang_L = value;
	return value;
}

