#include <iostream>
#include <cstdint>
#include <cstring>

extern "C" {
    int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size);
}

void functionB(int count);

void functionA(int count) {
    if (count <= 0) {
        return;
    }

    std::cout << "This is functionA, count: " << count << std::endl;

    functionB(count - 1);
}

void functionB(int count) {
    if (count <= 0) {
        return;
    }

    std::cout << "This is functionB, count: " << count << std::endl;

    functionA(count - 1);
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < sizeof(int)) {
        return 0;
    }

    int initialCount;
    memcpy(&initialCount, data, sizeof(int));

    // Limit the initialCount to avoid deep recursion
    initialCount = initialCount % 10;

    functionA(initialCount);
    return 0;
}