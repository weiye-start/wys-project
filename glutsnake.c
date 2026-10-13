#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <conio.h>
int main(void) {
    system("chcp 65001");  //规定字体防止出现乱码
    printf("\033[?25l");   //清除光标
    int i,j,x=0,y=2;
    printf("界面加载完成");
	while(1){
		char c = 0;
		printf("\033[2J\033[H");
		for(i=0;i<=20;i++){
			for(j=0;j<=20;j++){
				if (i==y && j==x){
					printf("\033[32m>>\033[0m");  //打印小方块
				}else{
					printf(" ");
				}	
			}
			printf("\n");  //输出完一行换行
	    }
	Sleep(300);
	if (_kbhit())
		c = _getch();
		if (c =='d') x++;      //按'd'键右移
		else if (c=='a') x--;  //按'a'键左移
		else if (c=='w') y--;  //按'w'键上移
		else if (c=='s') y++;  //按's'键下移
		else if (c=='q') break;//按'q'键退出
	}
    return 0;
}
