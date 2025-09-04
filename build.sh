#!/usr/bin/env bash
# 'set -e' waali line hata di gayi hai compatibility ke liye.

# Step 1: Zaroori Python packages install karna
pip install -r requirements.txt

# Step 2: PDF banane ke liye wkhtmltopdf install karna
apt-get update && apt-get install -y libxrender1 libfontconfig1 libxext6 wkhtmltopdf

