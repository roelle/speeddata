#include "relay.h"

/**
 * Encode long integer using AVRO zigzag + varint encoding
 * Matches Python avro.io.BinaryEncoder.write_long()
 */
void encode_long(int64_t value, uint8_t *buf, size_t *len) {
    /* Zigzag encoding: (n << 1) ^ (n >> 63) */
    uint64_t encoded = (value << 1) ^ (value >> 63);

    /* Variable-length encoding (7 bits per byte) */
    size_t idx = 0;
    while (encoded > 0x7F) {
        buf[idx++] = (uint8_t)((encoded & 0x7F) | 0x80);
        encoded >>= 7;
    }
    buf[idx++] = (uint8_t)(encoded & 0x7F);

    *len = idx;
}
