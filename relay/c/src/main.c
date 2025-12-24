#include "relay.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

static volatile int running = 1;

/**
 * Signal handler for graceful shutdown
 */
static void signal_handler(int sig) {
    (void)sig;
    running = 0;
    printf("\nShutting down...\n");
}

/**
 * Main relay loop
 */
int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <channel_name>\n", argv[0]);
        fprintf(stderr, "Example: %s example\n", argv[0]);
        return 1;
    }

    const char *channel_name = argv[1];

    /* Setup signal handlers */
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    /* Load configuration */
    relay_config_t config;
    if (load_config(channel_name, &config) != 0) {
        fprintf(stderr, "Failed to load configuration\n");
        return 1;
    }

    /* Setup sockets */
    relay_sockets_t socks;
    if (setup_sockets(&config, &socks) != 0) {
        fprintf(stderr, "Failed to setup sockets\n");
        return 1;
    }

    /* Initialize AVRO writer */
    avro_writer_t writer;
    if (avro_writer_init(&writer, config.output_dir) != 0) {
        fprintf(stderr, "Failed to initialize AVRO writer\n");
        close_sockets(&socks);
        return 1;
    }

    /* Initialize decimator */
    decimator_t decimator;
    decimator_init(&decimator, config.decimation_factor);

    /* Packet buffer */
    uint8_t packet[MAX_PACKET_SIZE];

    /* Multicast destination addresses */
    struct sockaddr_in mcast_full_addr;
    memset(&mcast_full_addr, 0, sizeof(mcast_full_addr));
    mcast_full_addr.sin_family = AF_INET;
    mcast_full_addr.sin_addr.s_addr = inet_addr(config.mcast_full_addr);
    mcast_full_addr.sin_port = htons(config.mcast_full_port);

    struct sockaddr_in mcast_dec_addr;
    if (config.decimation_enabled) {
        memset(&mcast_dec_addr, 0, sizeof(mcast_dec_addr));
        mcast_dec_addr.sin_family = AF_INET;
        mcast_dec_addr.sin_addr.s_addr = inet_addr(config.mcast_dec_addr);
        mcast_dec_addr.sin_port = htons(config.mcast_dec_port);
    }

    printf("\n=== SpeedData Relay Started ===\n");
    printf("Channel: %s\n", channel_name);
    printf("Ready to receive packets...\n\n");

    uint64_t packet_count = 0;

    /* Main relay loop */
    while (running) {
        /* Receive UDP packet */
        struct sockaddr_in src_addr;
        socklen_t src_len = sizeof(src_addr);
        ssize_t recv_len = recvfrom(
            socks.rx_sock,
            packet,
            MAX_PACKET_SIZE,
            0,
            (struct sockaddr *)&src_addr,
            &src_len
        );

        if (recv_len < 0) {
            if (running) {
                perror("recvfrom");
            }
            break;
        }

        packet_count++;
        printf("[%lu] Received %zd bytes from %s:%d\n",
               packet_count,
               recv_len,
               inet_ntoa(src_addr.sin_addr),
               ntohs(src_addr.sin_port));

        /* Write to AVRO file */
        if (avro_writer_write_block(&writer, packet, recv_len) != 0) {
            fprintf(stderr, "Failed to write AVRO block\n");
            break;
        }

        /* Relay to full-rate multicast */
        if (sendto(socks.mcast_full_sock, packet, recv_len, 0,
                   (struct sockaddr *)&mcast_full_addr,
                   sizeof(mcast_full_addr)) < 0) {
            perror("sendto(full)");
        }

        /* Relay to decimated multicast (if enabled and should send) */
        if (config.decimation_enabled && decimator_should_send(&decimator)) {
            if (sendto(socks.mcast_dec_sock, packet, recv_len, 0,
                       (struct sockaddr *)&mcast_dec_addr,
                       sizeof(mcast_dec_addr)) < 0) {
                perror("sendto(decimated)");
            }
            printf("  -> Sent to decimated multicast\n");
        }

        /* Check if file rotation needed */
        if (writer.current_size >= config.rotation_threshold) {
            if (avro_writer_rotate(&writer, config.output_dir) != 0) {
                fprintf(stderr, "Failed to rotate file\n");
                break;
            }
        }
    }

    /* Cleanup */
    printf("\nProcessed %lu packets\n", packet_count);
    avro_writer_close(&writer);
    close_sockets(&socks);

    return 0;
}
