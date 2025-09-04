#!/usr/bin/env bash
#
# Final build script with corrected line endings for Linux compatibility.
#

# Step 1: Install necessary Python packages
pip install -r requirements.txt

# Step 2: Install wkhtmltopdf and its dependencies
apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    wkhtmltopdf

