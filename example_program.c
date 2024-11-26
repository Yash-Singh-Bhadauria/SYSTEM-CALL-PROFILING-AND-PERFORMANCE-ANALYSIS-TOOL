#include <stdio.h>
#include <unistd.h>

int main() {
    printf("Hello, World!\n");
    write(1, "Writing to stdout\n", 19);
    return 0;
}
