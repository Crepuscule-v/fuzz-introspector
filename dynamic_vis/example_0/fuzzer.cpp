#include <stdint.h>
#include <stddef.h>

// 计算大写字母的数量
size_t count_uppercase_letters(const uint8_t *data, size_t size) {
    size_t count = 0;
    for (size_t i = 0; i < size; i++) {
        if (data[i] >= 'A' && data[i] <= 'Z') {
            count++;
        }
    }
    return count;
}

// libFuzzer需要的入口函数
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    count_uppercase_letters(data, size);
    return 0;
}