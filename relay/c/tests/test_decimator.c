#include "../include/relay.h"
#include <stdio.h>
#include <assert.h>

/**
 * Test decimator with factor=1 (no decimation)
 */
void test_decimator_no_decimation() {
    decimator_t dec;
    decimator_init(&dec, 1);

    /* Every packet should pass through */
    assert(decimator_should_send(&dec) == true);
    assert(decimator_should_send(&dec) == true);
    assert(decimator_should_send(&dec) == true);

    printf("✓ test_decimator_no_decimation passed\n");
}

/**
 * Test decimator with factor=5 (downsample by 5)
 */
void test_decimator_factor_5() {
    decimator_t dec;
    decimator_init(&dec, 5);

    /* First 4 packets should not send */
    assert(decimator_should_send(&dec) == false);  /* count=1 */
    assert(decimator_should_send(&dec) == false);  /* count=2 */
    assert(decimator_should_send(&dec) == false);  /* count=3 */
    assert(decimator_should_send(&dec) == false);  /* count=4 */

    /* 5th packet should send, then reset */
    assert(decimator_should_send(&dec) == true);   /* count=5 -> send + reset */

    /* Next cycle */
    assert(decimator_should_send(&dec) == false);  /* count=1 */
    assert(decimator_should_send(&dec) == false);  /* count=2 */
    assert(decimator_should_send(&dec) == false);  /* count=3 */
    assert(decimator_should_send(&dec) == false);  /* count=4 */
    assert(decimator_should_send(&dec) == true);   /* count=5 -> send */

    printf("✓ test_decimator_factor_5 passed\n");
}

/**
 * Test decimator reset behavior
 */
void test_decimator_reset() {
    decimator_t dec;
    decimator_init(&dec, 3);

    assert(decimator_should_send(&dec) == false);  /* count=1 */
    assert(decimator_should_send(&dec) == false);  /* count=2 */
    assert(decimator_should_send(&dec) == true);   /* count=3 -> send */

    /* Re-initialize (simulates restart) */
    decimator_init(&dec, 3);
    assert(dec.count == 0);
    assert(decimator_should_send(&dec) == false);  /* count=1 */

    printf("✓ test_decimator_reset passed\n");
}

int main() {
    printf("Running decimator tests...\n");
    test_decimator_no_decimation();
    test_decimator_factor_5();
    test_decimator_reset();
    printf("\nAll decimator tests passed!\n");
    return 0;
}
