#include <stdio.h>
int main(void){
    int x,x0,x1,y,y0,y1;
    printf("请输入x0和y0: \n");
    scanf("%d%d",&x0,&y0);
    printf("请输入x1和y1: \n");
    scanf("%d%d",&x1,&y1);
    printf("请输入x: \n");
    scanf("%d",&x);
    y = (y1-y0)/(x1-x0)*(x-x0) + y0;
    printf("%d时的气温是%d摄氏度",x,y);
    return 0;
}