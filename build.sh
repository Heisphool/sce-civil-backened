#!/usr/bin/env bash
#
# FINAL BUILD SCRIPT v3: Yeh script Windows errors ko theek karta hai aur apt-get file system issues ko bhi fix karta hai.
#

# Step 1: requirements.txt file ko Linux format mein convert karna
sed -i 's/\r$//' requirements.txt

# Step 2: Zaroori Python packages install karna
pip install -r requirements.txt

# Step 3: Apt-get ki locked/missing directory ko theek karna
rm -rf /var/lib/apt/lists/*
mkdir -p /var/lib/apt/lists/partial

# Step 4: PDF banane ke liye wkhtmltopdf aur uski dependencies ko install karna
apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    wkhtmltopdf

