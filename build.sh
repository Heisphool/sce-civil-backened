#!/usr/bin/env bash
#
# FINAL BUILD SCRIPT v4: Adds 'sudo' for admin permissions to fix file system errors.
#

# Step 1: requirements.txt file ko Linux format mein convert karna
sed -i 's/\r$//' requirements.txt

# Step 2: Zaroori Python packages install karna
pip install -r requirements.txt

# Step 3: Apt-get ki directory ko sudo (admin) permission se theek karna
sudo rm -rf /var/lib/apt/lists/*
sudo mkdir -p /var/lib/apt/lists/partial

# Step 4: PDF banane waale tools ko sudo (admin) permission se install karna
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    wkhtmltopdf

