#ifndef RELAY_H
#define RELAY_H

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <time.h>

/* Configuration limits */
#define MAX_PATH_LEN 256
#define MAX_NAME_LEN 64
#define MAX_PACKET_SIZE 65535
#define SYNC_MARKER_SIZE 16

/* Relay configuration */
typedef struct {
    char name[MAX_NAME_LEN];
    int rx_port;
    char output_dir[MAX_PATH_LEN];

    /* Multicast config */
    char mcast_full_addr[16];
    int mcast_full_port;
    char mcast_dec_addr[16];
    int mcast_dec_port;

    /* Decimation config */
    bool decimation_enabled;
    int decimation_factor;

    /* Rotation config */
    size_t rotation_threshold;  /* bytes */
} relay_config_t;

/* AVRO writer state */
typedef struct {
    FILE *fp;
    char filepath[MAX_PATH_LEN];
    size_t current_size;
    uint8_t sync_marker[SYNC_MARKER_SIZE];
} avro_writer_t;

/* Decimator state */
typedef struct {
    int factor;
    int count;
} decimator_t;

/* Socket set */
typedef struct {
    int rx_sock;          /* UDP receive socket */
    int mcast_full_sock;  /* Full-rate multicast */
    int mcast_dec_sock;   /* Decimated multicast */
} relay_sockets_t;

/* Function prototypes */

/* Configuration */
int load_config(const char *channel_name, relay_config_t *config);

/* AVRO writer */
int avro_writer_init(avro_writer_t *writer, const char *output_dir);
int avro_writer_write_block(avro_writer_t *writer, const uint8_t *data, size_t len);
int avro_writer_rotate(avro_writer_t *writer, const char *output_dir);
void avro_writer_close(avro_writer_t *writer);

/* Decimator */
void decimator_init(decimator_t *dec, int factor);
bool decimator_should_send(decimator_t *dec);

/* Sockets */
int setup_sockets(const relay_config_t *config, relay_sockets_t *socks);
void close_sockets(relay_sockets_t *socks);

/* Utils */
void encode_long(int64_t value, uint8_t *buf, size_t *len);

#endif /* RELAY_H */
