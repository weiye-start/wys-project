#include <stdio.h>
#include <windows.h>
#include <time.h>
int main(void) {
    printf("\033[?25l");
    
    
    int heart[5][5] = {
        {0,0,1,0,0},
        {0,0,1,0,0},
        {0,1,1,1,0},
        {1,1,1,1,1},
        {0,0,1,0,0}
    };
    time_t start_time = time(NULL);
    int offset = 0;
    int step = 1;
    
    while (1) {
        printf("\033[2J\033[H");
       
        for (int k = 0;k<offset;k++) {
            printf(" ");
        } 
        printf("\033[32m+---+---+---+\033[0m\n");
        for(int i=0;i<5;i++){
            for (int k=0;k<offset;k++){
            printf(" ");
        }
        
            for(int j=0;j<5;j++){
               if(heart[i][j] == 1){
                printf("\033[34m*\033[0m");
            } else {
                printf(" ");
            }
        }
        printf("\n");
        }
        for (int k = 0; k<offset;k++){
            printf(" ");
        }
        printf("\033[32m+---+---+---+\033[0m\n");
        
        Sleep(100);

        time_t current_time = time(NULL);
        if (current_time - start_time >=20){
            break;
        }

        offset += step;

        if (offset > 40 || offset < 0) {
            step = -step;
        }
    }
    printf("\033[?25");
    return 0;
}

