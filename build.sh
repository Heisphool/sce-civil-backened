#!/usr/bin/env bash
#
# FINAL BUILD SCRIPT v6: WeasyPrint ka istemal kar rahe hain, isliye apt-get ki ab zaroorat nahi.
#

# Step 1: requirements.txt file ko Linux format mein convert karna
sed -i 's/\r$//' requirements.txt

# Step 2: Zaroori Python packages install karna
pip install -r requirements.txt

echo "Build script safaltapoorvak poora hua. Koi system package install nahi kiya gaya."

