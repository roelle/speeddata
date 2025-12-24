#include "../include/relay.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

/**
 * Test AVRO long encoding
 */
void test_encode_long_simple() {
    uint8_t buf[10];
    size_t len;

    /* Test: encode_long(0) */
    encode_long(0, buf, &len);
    assert(len == 1);
    assert(buf[0] == 0x00);

    /* Test: encode_long(1) */
    encode_long(1, buf, &len);
    assert(len == 1);
    assert(buf[0] == 0x02);  /* zigzag: (1 << 1) = 2 */

    /* Test: encode_long(-1) */
    encode_long(-1, buf, &len);
    assert(len == 1);
    assert(buf[0] == 0x01);  /* zigzag: (-1 << 1) ^ (-1 >> 63) = 1 */

    printf("✓ test_encode_long_simple passed\n");
}

void test_encode_long_multi_byte() {
    uint8_t buf[10];
    size_t len;

    /* Test: encode_long(63) -> zigzag(126) -> 0x7E (single byte) */
    encode_long(63, buf, &len);
    assert(len == 1);
    assert(buf[0] == 0x7E);

    /* Test: encode_long(64) -> zigzag(128) -> needs 2 bytes */
    encode_long(64, buf, &len);
    assert(len == 2);
    assert(buf[0] == (0x80 | 0x00));  /* Continuation bit set */
    assert(buf[1] == 0x01);

    printf("✓ test_encode_long_multi_byte passed\n");
}

int main() {
    printf("Running AVRO utils tests...\n");
    test_encode_long_simple();
    test_encode_long_multi_byte();
    printf("\nAll utils tests passed!\n");
    return 0;
}
