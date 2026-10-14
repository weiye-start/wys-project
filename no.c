#include <stdio.h>
int main(){
	int i,j;
	for (i=1;i<=9;i++){
		for (j=1;j<=i;j++){
			if (i%2==1) printf("\033[33m%d*%d=%d\033[0m\t",i,j,i*j);
			else printf("\033[36m%d*%d=%d\033[0m\t",i,j,i*j);
		}
		printf("\n");
	}
	return 0;
}
