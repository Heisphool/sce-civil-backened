#!/usr/bin/env bash
# exit on error
set -e

# Install necessary Python packages
pip install -r requirements.txt

# Install wkhtmltopdf and its dependencies
apt-get update && apt-get install -y libxrender1 libfontconfig1 libxext6 wkhtmltopdf

