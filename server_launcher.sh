#!/bin/sh
# Run the server code

# Define the git repository name
repo="Server"

# Go to the repo's directory
cd /
cd home/pi/$repo

# Try to pull changes from the USB
sh git_update.sh

# Run the code
sudo python3 main.py

# Go back when done
cd /