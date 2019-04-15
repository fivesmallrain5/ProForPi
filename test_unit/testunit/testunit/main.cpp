#include "stdio.h"
#include <iostream>
#include "customCMDdwin.h"
extern struct Screenpara ScreenPara;
extern struct Screenoutcome ScreenOutCome;
using namespace std;

/*-------------------------------------------ģ�⴮���жϽ�������------��غ����붨�忪ʼ-------------------------------------------------------------------*/
u8 receive_str[100];     //���ջ�������,���USART_REC_LEN���ֽ� 
u8 uart_byte_count = 0;
u8 flag = 0x00;
u8 length = 0;
u8 state = 0x00;

//ģ���ж�   ����֡ͷ ��ȡ�������� 0x83  0x����  0x����
void receivedata(u8 data)
{
	u8 rec_data = data;
	switch (flag)
	{
	case  0x00: flag = rec_data == 0x5A ? 0x01 : 0x00; break;
	case  0x01: flag = rec_data == 0xA5 ? 0x02 : 0x00; break;
	case  0x02: flag = 0x03, length = rec_data; break;//��ȡ����ĳ���
	case  0x03:	flag = 0x00, uart_byte_count = 0x00, state = 0x01; break;//
	}
	if (state == 0x01)
	{
		if (uart_byte_count<50)//�ռ����ݣ�����������
		{
			receive_str[uart_byte_count] = rec_data;
			uart_byte_count++;
		}

		if (length == uart_byte_count)//һ֡�����ռ���ϣ���ʼ��������
		{
			uart_byte_count = 0x00;
			state = 0x00;
			for (int i = 0; i<length; i++)//���Ϊ����������
			{
				//printf("%x  ", receive_str[i]);
			}
			//cout << endl;
			checkCMD(length, receive_str);
		}
	}

}

/*----------------------------------ģ�⴮���жϽ�������------��غ����붨�����-------------------------------------------------------------------------*/



/*-----------------------------------ģ��AD-----------------��غ����붨�忪ʼ--------------------------------------------------------------*/

#define filterSize 5
#define peaksize   5//�洢��ֵ�ĸ�������ѡ����Ϊ�����ֵ
#define NumIsPeak	3//�ö��ٸ������жϷ�ֵ
/*�˲��õ�ȫ�ֱ���*/
u16 container[filterSize] = { 0 };
int index = 0;
/*��ֵ�õ�ȫ�ֱ���*/
u16 peak_container[peaksize] = { 0 };
u16  slidewindows[NumIsPeak] = { 0 };
u16 highestPeak = 0;
int peak_index = 0;
/*��������*/
u16 medfilter(u16 data);
u16 findpeaks(u16 data);




u16 medfilter(u16 data)
{
	int i = 0, sum = 0;
	u16 max_value = 0, min_value = 0;
	index = index >= filterSize ? 0 : index;
	container[index] = data;
	max_value = container[0];
	min_value = container[0];
	for (i = 0; i < filterSize; i++)
	{
		max_value = max_value > container[i] ? max_value : container[i];
		min_value = min_value < container[i] ? min_value : container[i];
		sum += container[i];
	}
	sum -= max_value;
	sum -= min_value;
	sum = (u16)(sum / (filterSize - 2));
	index += 1;
	return sum;
}



u16 findpeaks(u16 data)
{
	int i = 0, peakflag = 0;
	u16 max_value = 0;
	peak_index = peak_index >= peaksize ? 0 : peak_index;
	slidewindows[NumIsPeak - 1] = data;
	/*�ҷ�ֵ*/
	for (i = 0; i < (NumIsPeak - 1); i++)
	{
		if (i < ((NumIsPeak - 1) / 2))//�м��ǰ�벿���ж�
		{
			if (slidewindows[i] < slidewindows[i + 1])//�ж��Ƿ�����
			{
				peakflag = 1;
			}
			else
			{
				peakflag = 0;
				break;
			}
		}
		else//�ж��Ƿ��½��򲻱�
		{
			if (slidewindows[i] >= slidewindows[i + 1])
			{
				peakflag = 2;
			}
			else
			{
				peakflag = 0;
				break;
			}
		}

	}


	if (peakflag == 2)//�ҵ��˷�ֵ����ѡ���ķ�ֵ�����ֻ�������ֵ��ע��if�Σ�����highestPeak=slidewindows[((NumIsPeak - 1) / 2)];
	{
		peak_container[peak_index] = slidewindows[((NumIsPeak - 1) / 2)];
		peak_index += 1;
		max_value = peak_container[0];
		for (i = 0; i < peaksize; i++)
		{
			max_value = peak_container[i] > max_value ? peak_container[i] : max_value;
		}
		highestPeak = max_value;
	}

	for (i = 0; i < NumIsPeak - 1; i++)//��������
	{
		slidewindows[i] = slidewindows[i + 1];
	}

	return highestPeak;
}
/*-----------------------------------ģ��AD-----------------��غ����붨�����--------------------------------------------------------------*/


int main()
{   //������Ļ���͵�����
	u8 usart_cmd[] = { 0x5A ,0xA5,0x03,0x01,0x02,0x03,
		0x5A ,0xA5,0x04,0x01,0x02,0x03,0x5A,
		0x5A,
		0x5A ,0xA5,0x03,0x01,0x02,0x03,
		0x5A ,0xA5,0x01, 0x02,
		0x03,
		0x5A,0xA5,0x0C,0x83,0x3F,0xFF,0x04,0x5A,0x03,0x34,0x35,0x36,0xFF,0xFF,0xFF,//456
		0x5A,0xA5,0x0E,0x83,0x3F,0xFF,0x04,0x5A,0x05,0x2D,0x34,0x35,0x2E,0x36,0xFF,0xFF,0xFF,//-45.6
		
		0x5A,0xA5,0x0E, 0x83,0x3F,0xFF,   0x04,0x5A,0x05,  0x2E,0x2E,0x34,0x35,0x36,0xFF,0xFF,0xFF,//..456

		0x5A,0xA5,0x0E, 0x83,0x3F,0xFF,  0x04,0x5A,0x06,   0x39,0x2E,0x38,0x30,0x36,0x35,0xFF,0xFF,//ϵ��k9.8065
		0x5A,0xA5,0x0C, 0x83,0x40,0x1F,  0x04,0x5A,0x05,   0x30,0x2E,0x30,0x30,0x32,0xFF,//����ѹ���ĵ�ַ 0.002
		0x5A,0xA5,0x0A, 0x83,0x40,0x3F,  0x04,0x5A,0x02,   0x32,0xFF,0xFF,0xFF,//��������ĵ�ַ  2
		0x5A,0xA5,0x0D, 0x83,0x3F,0xF1,  0x04,0x5A,0x04,  0x2E,0x34,0x35,0x36,0xFF,0xFF,0xFF,//�����ַ����.456
		0x5A,0xA5,0x0C, 0x83,0x40,0x5F,  0x04,0x5A,0x03,  0x34,0x35,0x36,0xFF,0xFF,0xFF,//����ѹ���ĵ�ַ 456
		0x5A,0xA5,0x0A, 0x83,0x40,0x7F,  0x04,0x5A,0x01,  0x38,0xFF,0xFF,0xFF,//���������ĵ�ַ 8

	};
	//AD���͵�����
	u16 AD_data[] = { 0x0001, 0x0003, 0x0002, 0x0005,  0x00f6, 0x0007,0xffff, 0xffff, 0xffff, 0x0002, 0x0003, 0x0001, 0x000d ,
		0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002,0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002 ,
		0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002,0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002 ,
		0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002,0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002 ,
		0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002,0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002 ,
		0x0009, 0x00bb, 0x00bb, 0x00bb ,0x00bb, 0x0003, 0x000b, 0x0002,0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002 ,
		0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002,0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002 ,
		0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002,0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002 ,
		0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x00bb, 0x0002,0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002 ,
		0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002,0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002 ,
		0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x00ba, 0x00bb, 0x00ba,0x0009, 0x0003, 0x0005, 0x0002 ,0x000a, 0x0003, 0x000b, 0x0002 };
	int AD_data_lenths = sizeof(AD_data) / sizeof(u16);
	int usart_cmd_lenths = sizeof(usart_cmd) / sizeof(u8);

	int j = 0;
	//ģ�⴮����Ļ�������������
	for (j = 0; j<usart_cmd_lenths ; j++)
	{
		receivedata(usart_cmd[j]);//�������ֵ��ScreenPara
	}
	printf("������Ļ�Ĳ���Ϊ��----------------------------------------\n");
	printf("ϵ��k:%f\n", ScreenPara.s_XiShu_K);
	printf("����ѹ��:%f\n", ScreenPara.s_RongQiYaLi_Pr);
	printf("�������:%f\n", ScreenPara.s_FaBanMianJi_A);
	printf("����ѹ��:%f\n", ScreenPara.s_ZhengDingYaLi_Pset2);
	printf("��������:%f\n", ScreenPara.s_TanHuangZenLiang_Q);
	printf("---------------------------------------------------------\n\n");

	calculate_TiShengLi_F();//����Ļ������������
	union Screen_uint32  temp;
	temp.s_uint32 = SCREEN_FLOAT2U32(ScreenOutCome.s_out_TiShengLi_F);
	printf("����������Ϊ��---------------------------------------------------------\n");
	printf("%f\n", ScreenOutCome.s_out_TiShengLi_F);
	ChangeScreenVariable((u16)(ADDR_TiShengLi_F),temp.s_char );//�����������͵���Ļ
	printf("-------------------------------------------------------------------\n\n");


	//AD�ɼ������ݣ���Ҫ��Ϊ�˻�÷�ֵ
	u16 beforepeaks = 0;
	for (j = 0; j < AD_data_lenths; j++)
	{
		u16 temppeaks = findpeaks(medfilter(AD_data[j]));
		ScreenOutCome.s_out_FengZhi_F = temppeaks;
		if (beforepeaks != temppeaks)//�˲�֮���ҷ�ֵ,һ���µķ�ֵ�����ͼ���
		{
			printf("�����·�ֵ%x ���������ѹ��Pset1�͵�����L��--------------------------\n", temppeaks);
			calculate_ZhengDingYaLi_Pset1();//���ʽ�ӵļ�����ҪAD��ֵ
			temp.s_uint32 = SCREEN_FLOAT2U32(ScreenOutCome.s_out_ZhengDingYaLi_Pset1);
			printf("����ѹ��Pset1:%f\n", ScreenOutCome.s_out_ZhengDingYaLi_Pset1);
			ChangeScreenVariable((u16)(ADDR_ZhengDingYaLi_Pset1), temp.s_char);//�����������͵���Ļ

			calculate_TiaoZhengLiang_L();//��calculate_ZhengDingYaLi_Pset1()�ļ���������Ļ�������������
			temp.s_uint32 = SCREEN_FLOAT2U32(ScreenOutCome.s_out_TiaoZhengLiang_L);
			printf("����ѹ��������L:%f\n", ScreenOutCome.s_out_TiaoZhengLiang_L);
			ChangeScreenVariable((u16)(ADDR_TiaoZhengLiang_L), temp.s_char);//�����������͵���Ļ
			printf("-----------------------------------------------------------\n\n");
			beforepeaks = temppeaks;
		}
	}

	

	




	
	system("pause");

}








