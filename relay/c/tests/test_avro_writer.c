#include "../include/relay.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <sys/stat.h>
#include <unistd.h>

#define TEST_DIR "/tmp/relay_test"

/**
 * Helper: check if file exists
 */
static int file_exists(const char *path) {
    struct stat st;
    return stat(path, &st) == 0;
}

/**
 * Helper: get file size
 */
static size_t get_file_size(const char *path) {
    struct stat st;
    if (stat(path, &st) != 0) {
        return 0;
    }
    return st.st_size;
}

/**
 * Test AVRO writer initialization
 */
void test_avro_writer_init() {
    avro_writer_t writer;

    /* Initialize writer */
    int ret = avro_writer_init(&writer, TEST_DIR);
    assert(ret == 0);
    assert(writer.fp != NULL);
    assert(writer.current_size == 0);

    /* Check file was created */
    assert(file_exists(writer.filepath));

    /* Cleanup */
    avro_writer_close(&writer);

    printf("✓ test_avro_writer_init passed\n");
}

/**
 * Test AVRO block writing
 */
void test_avro_writer_write_block() {
    avro_writer_t writer;
    avro_writer_init(&writer, TEST_DIR);

    /* Write a block */
    uint8_t test_data[] = {0x01, 0x02, 0x03, 0x04, 0x05};
    size_t test_len = sizeof(test_data);

    int ret = avro_writer_write_block(&writer, test_data, test_len);
    assert(ret == 0);

    /* Verify size increased */
    assert(writer.current_size > 0);

    /* Expected: count_varint + len_varint + data + sync_marker */
    /* Minimum: 1 + 1 + 5 + 16 = 23 bytes */
    assert(writer.current_size >= 23);

    /* Cleanup */
    avro_writer_close(&writer);

    printf("✓ test_avro_writer_write_block passed\n");
}

/**
 * Test AVRO writer multiple blocks
 */
void test_avro_writer_multiple_blocks() {
    avro_writer_t writer;
    avro_writer_init(&writer, TEST_DIR);

    /* Write 10 blocks */
    uint8_t data[100];
    memset(data, 0xAB, sizeof(data));

    for (int i = 0; i < 10; i++) {
        int ret = avro_writer_write_block(&writer, data, sizeof(data));
        assert(ret == 0);
    }

    /* Verify file grew */
    assert(writer.current_size > 1000);

    /* Verify file on disk matches tracked size */
    size_t file_size = get_file_size(writer.filepath);
    assert(file_size == writer.current_size);

    /* Cleanup */
    avro_writer_close(&writer);

    printf("✓ test_avro_writer_multiple_blocks passed\n");
}

/**
 * Test AVRO writer rotation
 */
void test_avro_writer_rotation() {
    avro_writer_t writer;
    avro_writer_init(&writer, TEST_DIR);

    /* Save original filepath */
    char first_file[MAX_PATH_LEN];
    strcpy(first_file, writer.filepath);

    /* Write some data */
    uint8_t data[100];
    avro_writer_write_block(&writer, data, sizeof(data));

    /* Wait 1 second to ensure different timestamp */
    sleep(1);

    /* Rotate */
    int ret = avro_writer_rotate(&writer, TEST_DIR);
    assert(ret == 0);

    /* Check new file was created */
    assert(strcmp(writer.filepath, first_file) != 0);
    assert(file_exists(writer.filepath));
    assert(writer.current_size == 0);

    /* Old file should still exist */
    assert(file_exists(first_file));

    /* Cleanup */
    avro_writer_close(&writer);

    printf("✓ test_avro_writer_rotation passed\n");
}

/**
 * Test sync marker consistency
 */
void test_sync_marker() {
    avro_writer_t writer;
    avro_writer_init(&writer, TEST_DIR);

    /* Expected sync marker (from Python implementation) */
    uint8_t expected[SYNC_MARKER_SIZE] = {
        0xa4, 0x8a, 0x1e, 0x90, 0x05, 0x04, 0x24, 0x78,
        0x0a, 0x68, 0x33, 0x7f, 0xc2, 0x50, 0x95, 0x63
    };

    /* Verify sync marker matches */
    assert(memcmp(writer.sync_marker, expected, SYNC_MARKER_SIZE) == 0);

    /* Cleanup */
    avro_writer_close(&writer);

    printf("✓ test_sync_marker passed\n");
}

int main() {
    printf("Running AVRO writer tests...\n");

    /* Create test directory */
    mkdir(TEST_DIR, 0755);

    test_avro_writer_init();
    test_avro_writer_write_block();
    test_avro_writer_multiple_blocks();
    test_avro_writer_rotation();
    test_sync_marker();

    printf("\nAll AVRO writer tests passed!\n");

    /* Cleanup test directory */
    system("rm -rf " TEST_DIR);

    return 0;
}
