#!/usr/bin/env bash
#
# FINAL BUILD SCRIPT v5: Correct approach for Render's container environment without sudo.
#

# Step 1: Fix potential Windows line ending issues in requirements.txt
sed -i 's/\r$//' requirements.txt

# Step 2: Install Python packages
pip install -r requirements.txt

# Step 3: Install system dependencies for wkhtmltopdf using standard apt-get
# Is environment mein sudo command nahi hai, aur iski zaroorat bhi nahi hai.
apt-get update
apt-get install -y libxrender1 libfontconfig1 libxext6 wkhtmltopdf

