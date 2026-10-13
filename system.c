#include <stdlib.h>
int system (const char *command);
int main (void) {
	system("date +%A");
	system("gcc --version");
}
	