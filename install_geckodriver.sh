#!/bin/bash

# GeckoDriver Install Script for Raspberry Pi 4B
# Requires internet connection and sudo privileges

# Get latest version from GitHub API
LATEST_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep -oP '"tag_name": "\K[^"]*')

# Check architecture
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    ARCHITECTURE="aarch64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

# Construct download URL
DOWNLOAD_URL="https://github.com/mozilla/geckodriver/releases/download/$LATEST_VERSION/geckodriver-$LATEST_VERSION-linux-$ARCHITECTURE.tar.gz"

# Installation directory
INSTALL_DIR="/usr/local/bin"

# Download and extract GeckoDriver
echo "Installing GeckoDriver $LATEST_VERSION for $ARCH..."
echo "Downloading from: $DOWNLOAD_URL"
wget -q $DOWNLOAD_URL -O geckodriver.tar.gz

# Check if download succeeded
if [ $? -ne 0 ]; then
    echo "Failed to download GeckoDriver"
    exit 1
fi

# Extract the file
tar -xf geckodriver.tar.gz

# Install to system
sudo mv geckodriver $INSTALL_DIR
sudo chmod +x $INSTALL_DIR/geckodriver

# Cleanup
rm geckodriver.tar.gz

# Verify installation
if command -v geckodriver &> /dev/null; then
    echo "GeckoDriver installed successfully!"
    geckodriver --version
else
    echo "Installation failed - check permissions and try again"
    exit 1
fi
