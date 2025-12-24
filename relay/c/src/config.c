#include "relay.h"
#include <string.h>
#include <stdlib.h>

/**
 * Load configuration from defaults and environment
 * For v0.4, we use hardcoded defaults matching relay.yaml + global.yaml
 * Python orchestrator can override via environment variables
 */
int load_config(const char *channel_name, relay_config_t *config) {
    /* Set channel name */
    strncpy(config->name, channel_name, MAX_NAME_LEN - 1);
    config->name[MAX_NAME_LEN - 1] = '\0';

    /* Default ports (from config/relay.yaml) */
    config->rx_port = 26000;  /* example channel */

    /* Multicast addresses (from config/global.yaml) */
    strncpy(config->mcast_full_addr, "239.1.1.1", sizeof(config->mcast_full_addr));
    config->mcast_full_port = 6000;
    strncpy(config->mcast_dec_addr, "239.1.1.2", sizeof(config->mcast_dec_addr));
    config->mcast_dec_port = 6001;

    /* Decimation (from config/relay.yaml) */
    config->decimation_enabled = true;
    config->decimation_factor = 5;

    /* Rotation threshold (from config/relay.yaml) */
    config->rotation_threshold = 50 * 1024 * 1024;  /* 50 MB */

    /* Output directory (from config/global.yaml) */
    strncpy(config->output_dir, "./data", MAX_PATH_LEN - 1);

    /* Override from environment variables if set */
    char *env_port = getenv("RELAY_RX_PORT");
    if (env_port) {
        config->rx_port = atoi(env_port);
    }

    char *env_output = getenv("RELAY_OUTPUT_DIR");
    if (env_output) {
        strncpy(config->output_dir, env_output, MAX_PATH_LEN - 1);
    }

    char *env_dec_factor = getenv("RELAY_DECIMATION_FACTOR");
    if (env_dec_factor) {
        config->decimation_factor = atoi(env_dec_factor);
    }

    char *env_dec_enabled = getenv("RELAY_DECIMATION_ENABLED");
    if (env_dec_enabled) {
        config->decimation_enabled = (strcmp(env_dec_enabled, "true") == 0 ||
                                      strcmp(env_dec_enabled, "1") == 0);
    }

    printf("Configuration loaded for channel '%s':\n", config->name);
    printf("  RX Port: %d\n", config->rx_port);
    printf("  Output Dir: %s\n", config->output_dir);
    printf("  Decimation: %s (factor: %d)\n",
           config->decimation_enabled ? "enabled" : "disabled",
           config->decimation_factor);

    return 0;
}
