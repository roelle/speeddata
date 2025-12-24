#include "relay.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

/**
 * Setup UDP receive socket
 */
static int setup_rx_socket(int port) {
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        perror("socket(rx)");
        return -1;
    }

    /* Bind to localhost:port */
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    addr.sin_port = htons(port);

    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(sock);
        return -1;
    }

    printf("Listening on 127.0.0.1:%d\n", port);
    return sock;
}

/**
 * Setup multicast send socket
 */
static int setup_mcast_socket(const char *addr, int port) {
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        perror("socket(mcast)");
        return -1;
    }

    /* Set multicast TTL */
    unsigned char ttl = 2;
    if (setsockopt(sock, IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof(ttl)) < 0) {
        perror("setsockopt(TTL)");
        close(sock);
        return -1;
    }

    printf("Multicast sender: %s:%d\n", addr, port);
    return sock;
}

/**
 * Setup all relay sockets
 */
int setup_sockets(const relay_config_t *config, relay_sockets_t *socks) {
    /* RX socket */
    socks->rx_sock = setup_rx_socket(config->rx_port);
    if (socks->rx_sock < 0) {
        return -1;
    }

    /* Full-rate multicast */
    socks->mcast_full_sock = setup_mcast_socket(
        config->mcast_full_addr,
        config->mcast_full_port
    );
    if (socks->mcast_full_sock < 0) {
        close(socks->rx_sock);
        return -1;
    }

    /* Decimated multicast (if enabled) */
    if (config->decimation_enabled) {
        socks->mcast_dec_sock = setup_mcast_socket(
            config->mcast_dec_addr,
            config->mcast_dec_port
        );
        if (socks->mcast_dec_sock < 0) {
            close(socks->rx_sock);
            close(socks->mcast_full_sock);
            return -1;
        }
    } else {
        socks->mcast_dec_sock = -1;
    }

    return 0;
}

/**
 * Close all sockets
 */
void close_sockets(relay_sockets_t *socks) {
    if (socks->rx_sock >= 0) {
        close(socks->rx_sock);
    }
    if (socks->mcast_full_sock >= 0) {
        close(socks->mcast_full_sock);
    }
    if (socks->mcast_dec_sock >= 0) {
        close(socks->mcast_dec_sock);
    }
}
