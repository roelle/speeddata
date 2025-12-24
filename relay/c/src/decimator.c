#include "relay.h"

/**
 * Initialize decimator
 */
void decimator_init(decimator_t *dec, int factor) {
    dec->factor = factor;
    dec->count = 0;
}

/**
 * Check if current packet should be sent to decimated multicast
 * Returns true every Nth packet (downsampling)
 */
bool decimator_should_send(decimator_t *dec) {
    if (dec->factor <= 1) {
        return true;  /* No decimation */
    }

    dec->count++;
    if (dec->count >= dec->factor) {
        dec->count = 0;
        return true;
    }

    return false;
}
