#include <stdio.h>
#include <stdlib.h>
int main(void) {
    system("chcp 65001");
    int i,j;
    int a[5][5] = {
        {1,1,1,1,1},
        {1,0,0,0,0},
        {1,1,1,1,0},
        {0,0,0,1,0},
        {1,1,1,1,0}
    };
    for (i=0;i<5;i++) {
        for (j=0;j<5;j++) {
            if (a[i][j]==1)
               printf("\033[32m■\033[0m");
            else
               printf(" ");
            if (j>=4)
                printf("\n");
        }
    }
    system("pause");
    return 0;
}
