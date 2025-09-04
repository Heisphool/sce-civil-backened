#!/usr/bin/env bash
#
# FINAL BUILD SCRIPT: Yeh script Windows line ending errors ko automatically theek kar deta hai.
#

# Step 1: requirements.txt file ko Linux format mein convert karna
# Yeh command file se invisible Windows characters (\r) ko hata degi.
sed -i 's/\r$//' requirements.txt

# Step 2: Zaroori Python packages install karna
pip install -r requirements.txt

# Step 3: PDF banane ke liye wkhtmltopdf aur uski dependencies ko ek saath install karna
apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    wkhtmltopdf

