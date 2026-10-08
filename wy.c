#define pi 3.14
#include <stdio.h>
int main(void) {
    int a[3][3],i,j,x=0;
    for(i=0;i<3;i++)
        for(j=0;j<3;j++){
            a[i][j] = x;
            x++;
        }
    printf("\033[34moutput:\033[0m\n");
    for(i=0;i<3;i++){
        for(j=0;j<3;j++)
            printf("\033[35m%4d\033[0m",a[i][j]);
        printf("\n");
    }
}

