#!/bin/bash
# SpeedData Configuration Deployment Script
# Synchronizes config/ directory to target hosts

set -e

# Configuration
CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_PATH="/etc/speeddata"

# Update from git
echo "Pulling latest config from git..."
cd "$CONFIG_DIR/.."
git pull origin main || echo "Warning: git pull failed (may not be in repo)"

# Deploy to target hosts
# Modify these for your deployment
HOSTS=(
    "localhost"
    # "relay-host"
    # "stripchart-host"
    # "pivot-host"
)

for host in "${HOSTS[@]}"; do
    echo "Deploying to $host..."
    if [ "$host" = "localhost" ]; then
        # Local deployment
        sudo mkdir -p "$TARGET_PATH"
        sudo cp -r "$CONFIG_DIR"/*.yaml "$TARGET_PATH/"
        echo "  ✓ Deployed to $TARGET_PATH"
    else
        # Remote deployment via rsync
        rsync -av --delete "$CONFIG_DIR"/*.yaml "$host:$TARGET_PATH/"
        echo "  ✓ Deployed to $host:$TARGET_PATH"
    fi
done

echo "Deployment complete!"
echo "Remember to restart services for changes to take effect."
