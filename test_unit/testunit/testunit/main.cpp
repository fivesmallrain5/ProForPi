#include "stdio.h"
#include <iostream>
#include "customCMDdwin.h"
extern struct Screenpara ScreenPara;
extern struct Screenoutcome ScreenOutCome;
using namespace std;

/*-------------------------------------------模拟串口中断解析数据------相关函数与定义开始-------------------------------------------------------------------*/
u8 receive_str[100];     //接收缓存数组,最大USART_REC_LEN个字节 
u8 uart_byte_count = 0;
u8 flag = 0x00;
u8 length = 0;
u8 state = 0x00;

//模拟中断   解析帧头 提取有用数据 0x83  0x长度  0x数据
void receivedata(u8 data)
{
	u8 rec_data = data;
	switch (flag)
	{
	case  0x00: flag = rec_data == 0x5A ? 0x01 : 0x00; break;
	case  0x01: flag = rec_data == 0xA5 ? 0x02 : 0x00; break;
	case  0x02: flag = 0x03, length = rec_data; break;//获取命令的长度
	case  0x03:	flag = 0x00, uart_byte_count = 0x00, state = 0x01; break;//
	}
	if (state == 0x01)
	{
		if (uart_byte_count<50)//收集数据，不包含长度
		{
			receive_str[uart_byte_count] = rec_data;
			uart_byte_count++;
		}

		if (length == uart_byte_count)//一帧数据收集完毕，开始处理数据
		{
			uart_byte_count = 0x00;
			state = 0x00;
			for (int i = 0; i<length; i++)//输出为解析的命令
			{
				//printf("%x  ", receive_str[i]);
			}
			//cout << endl;
			checkCMD(length, receive_str);
		}
	}

}

/*----------------------------------模拟串口中断解析数据------相关函数与定义结束-------------------------------------------------------------------------*/



/*-----------------------------------模拟AD-----------------相关函数与定义开始--------------------------------------------------------------*/

#define filterSize 5
#define peaksize   5//存储峰值的个数，挑选最大的为输出峰值
#define NumIsPeak	3//用多少个点来判断峰值
/*滤波用的全局变量*/
u16 container[filterSize] = { 0 };
int index = 0;
/*峰值用的全局变量*/
u16 peak_container[peaksize] = { 0 };
u16  slidewindows[NumIsPeak] = { 0 };
u16 highestPeak = 0;
int peak_index = 0;
/*函数声明*/
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
	/*找峰值*/
	for (i = 0; i < (NumIsPeak - 1); i++)
	{
		if (i < ((NumIsPeak - 1) / 2))//中间点前半部分判断
		{
			if (slidewindows[i] < slidewindows[i + 1])//判断是否上升
			{
				peakflag = 1;
			}
			else
			{
				peakflag = 0;
				break;
			}
		}
		else//判断是否下降或不变
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


	if (peakflag == 2)//找到了峰值，挑选最大的峰值，如果只想输出峰值就注释if段，改用highestPeak=slidewindows[((NumIsPeak - 1) / 2)];
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

	for (i = 0; i < NumIsPeak - 1; i++)//左移数据
	{
		slidewindows[i] = slidewindows[i + 1];
	}

	return highestPeak;
}
/*-----------------------------------模拟AD-----------------相关函数与定义结束--------------------------------------------------------------*/


int main()
{   //串口屏幕发送的数据
	u8 usart_cmd[] = { 0x5A ,0xA5,0x03,0x01,0x02,0x03,
		0x5A ,0xA5,0x04,0x01,0x02,0x03,0x5A,
		0x5A,
		0x5A ,0xA5,0x03,0x01,0x02,0x03,
		0x5A ,0xA5,0x01, 0x02,
		0x03,
		0x5A,0xA5,0x0C,0x83,0x3F,0xFF,0x04,0x5A,0x03,0x34,0x35,0x36,0xFF,0xFF,0xFF,//456
		0x5A,0xA5,0x0E,0x83,0x3F,0xFF,0x04,0x5A,0x05,0x2D,0x34,0x35,0x2E,0x36,0xFF,0xFF,0xFF,//-45.6
		
		0x5A,0xA5,0x0E, 0x83,0x3F,0xFF,   0x04,0x5A,0x05,  0x2E,0x2E,0x34,0x35,0x36,0xFF,0xFF,0xFF,//..456

		0x5A,0xA5,0x0E, 0x83,0x3F,0xFF,  0x04,0x5A,0x06,   0x39,0x2E,0x38,0x30,0x36,0x35,0xFF,0xFF,//系数k9.8065
		0x5A,0xA5,0x0C, 0x83,0x40,0x1F,  0x04,0x5A,0x05,   0x30,0x2E,0x30,0x30,0x32,0xFF,//容器压力的地址 0.002
		0x5A,0xA5,0x0A, 0x83,0x40,0x3F,  0x04,0x5A,0x02,   0x32,0xFF,0xFF,0xFF,//阀瓣面积的地址  2
		0x5A,0xA5,0x0D, 0x83,0x3F,0xF1,  0x04,0x5A,0x04,  0x2E,0x34,0x35,0x36,0xFF,0xFF,0xFF,//错误地址数据.456
		0x5A,0xA5,0x0C, 0x83,0x40,0x5F,  0x04,0x5A,0x03,  0x34,0x35,0x36,0xFF,0xFF,0xFF,//整定压力的地址 456
		0x5A,0xA5,0x0A, 0x83,0x40,0x7F,  0x04,0x5A,0x01,  0x38,0xFF,0xFF,0xFF,//弹簧增量的地址 8

	};
	//AD发送的数据
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
	//模拟串口屏幕发送数据与解析
	for (j = 0; j<usart_cmd_lenths ; j++)
	{
		receivedata(usart_cmd[j]);//解析命令赋值给ScreenPara
	}
	printf("输入屏幕的参数为：----------------------------------------\n");
	printf("系数k:%f\n", ScreenPara.s_XiShu_K);
	printf("容器压力:%f\n", ScreenPara.s_RongQiYaLi_Pr);
	printf("阀瓣面积:%f\n", ScreenPara.s_FaBanMianJi_A);
	printf("整定压力:%f\n", ScreenPara.s_ZhengDingYaLi_Pset2);
	printf("弹簧增量:%f\n", ScreenPara.s_TanHuangZenLiang_Q);
	printf("---------------------------------------------------------\n\n");

	calculate_TiShengLi_F();//由屏幕的输入参数算出
	union Screen_uint32  temp;
	temp.s_uint32 = SCREEN_FLOAT2U32(ScreenOutCome.s_out_TiShengLi_F);
	printf("提升力计算为：---------------------------------------------------------\n");
	printf("%f\n", ScreenOutCome.s_out_TiShengLi_F);
	ChangeScreenVariable((u16)(ADDR_TiShengLi_F),temp.s_char );//将计算结果发送到屏幕
	printf("-------------------------------------------------------------------\n\n");


	//AD采集的数据，主要是为了获得峰值
	u16 beforepeaks = 0;
	for (j = 0; j < AD_data_lenths; j++)
	{
		u16 temppeaks = findpeaks(medfilter(AD_data[j]));
		ScreenOutCome.s_out_FengZhi_F = temppeaks;
		if (beforepeaks != temppeaks)//滤波之后找峰值,一旦新的峰值产生就计算
		{
			printf("出现新峰值%x 计算的整定压力Pset1和调整量L：--------------------------\n", temppeaks);
			calculate_ZhengDingYaLi_Pset1();//这个式子的计算需要AD峰值
			temp.s_uint32 = SCREEN_FLOAT2U32(ScreenOutCome.s_out_ZhengDingYaLi_Pset1);
			printf("整定压力Pset1:%f\n", ScreenOutCome.s_out_ZhengDingYaLi_Pset1);
			ChangeScreenVariable((u16)(ADDR_ZhengDingYaLi_Pset1), temp.s_char);//将计算结果发送到屏幕

			calculate_TiaoZhengLiang_L();//由calculate_ZhengDingYaLi_Pset1()的计算结果和屏幕的输入参数决定
			temp.s_uint32 = SCREEN_FLOAT2U32(ScreenOutCome.s_out_TiaoZhengLiang_L);
			printf("整定压力调整量L:%f\n", ScreenOutCome.s_out_TiaoZhengLiang_L);
			ChangeScreenVariable((u16)(ADDR_TiaoZhengLiang_L), temp.s_char);//将计算结果发送到屏幕
			printf("-----------------------------------------------------------\n\n");
			beforepeaks = temppeaks;
		}
	}

	

	




	
	system("pause");

}








