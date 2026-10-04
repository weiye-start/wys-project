#include <stdio.h>
int main(){
    int a,a1,a2,a3,a4;
    scanf("%d",&a);
    a4 = a%10;
    a3 = a/10%10;
    a2 = a/100%10;
    a1 = a/1000%10;
    printf("%d\t%d\t%d\t%d",a1,a2,a3,a4);
    getchar();
    getchar();
    return 0;
}