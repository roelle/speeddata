#include "relay.h"
#include <string.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <errno.h>

/* Fixed AVRO sync marker (must match Python implementation) */
static const uint8_t FIXED_SYNC_MARKER[SYNC_MARKER_SIZE] = {
    0xa4, 0x8a, 0x1e, 0x90, 0x05, 0x04, 0x24, 0x78,
    0x0a, 0x68, 0x33, 0x7f, 0xc2, 0x50, 0x95, 0x63
};

/**
 * Create output directory if it doesn't exist
 */
static int ensure_dir(const char *path) {
    struct stat st = {0};
    if (stat(path, &st) == -1) {
        if (mkdir(path, 0755) == -1 && errno != EEXIST) {
            perror("mkdir");
            return -1;
        }
    }
    return 0;
}

/**
 * Initialize AVRO writer with new file
 */
int avro_writer_init(avro_writer_t *writer, const char *output_dir) {
    if (ensure_dir(output_dir) != 0) {
        return -1;
    }

    /* Generate filename: data_<timestamp>.avro */
    time_t now = time(NULL);
    snprintf(writer->filepath, MAX_PATH_LEN, "%s/data_%ld.avro", output_dir, now);

    writer->fp = fopen(writer->filepath, "wb");
    if (!writer->fp) {
        perror("fopen");
        return -1;
    }

    writer->current_size = 0;
    memcpy(writer->sync_marker, FIXED_SYNC_MARKER, SYNC_MARKER_SIZE);

    printf("Created AVRO file: %s\n", writer->filepath);
    return 0;
}

/**
 * Write AVRO block (matching Python format):
 * - object count (long, always 1)
 * - byte count (long, length of data)
 * - data (raw bytes)
 * - sync marker (16 bytes)
 */
int avro_writer_write_block(avro_writer_t *writer, const uint8_t *data, size_t len) {
    if (!writer->fp) {
        fprintf(stderr, "AVRO writer not initialized\n");
        return -1;
    }

    /* Encode object count = 1 */
    uint8_t count_buf[10];
    size_t count_len;
    encode_long(1, count_buf, &count_len);
    if (fwrite(count_buf, 1, count_len, writer->fp) != count_len) {
        perror("fwrite count");
        return -1;
    }

    /* Encode byte count = data length */
    uint8_t len_buf[10];
    size_t len_len;
    encode_long((int64_t)len, len_buf, &len_len);
    if (fwrite(len_buf, 1, len_len, writer->fp) != len_len) {
        perror("fwrite length");
        return -1;
    }

    /* Write data */
    if (fwrite(data, 1, len, writer->fp) != len) {
        perror("fwrite data");
        return -1;
    }

    /* Write sync marker */
    if (fwrite(writer->sync_marker, 1, SYNC_MARKER_SIZE, writer->fp) != SYNC_MARKER_SIZE) {
        perror("fwrite sync");
        return -1;
    }

    /* Update size tracking */
    writer->current_size += count_len + len_len + len + SYNC_MARKER_SIZE;

    /* Flush to disk */
    fflush(writer->fp);

    return 0;
}

/**
 * Rotate to new file
 */
int avro_writer_rotate(avro_writer_t *writer, const char *output_dir) {
    printf("Rotating file: %s (size: %zu bytes)\n", writer->filepath, writer->current_size);

    avro_writer_close(writer);
    return avro_writer_init(writer, output_dir);
}

/**
 * Close AVRO writer
 */
void avro_writer_close(avro_writer_t *writer) {
    if (writer->fp) {
        fclose(writer->fp);
        writer->fp = NULL;
    }
}
