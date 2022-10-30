#!/bin/sh
# Try to update from the git repositories on the USB flashdrive for the server

# Define the git repositories
server="Server"
node="Node"

# Ensure that the current directory is home/pi
cd /
cd home/pi

# Mount the USB with 1000 user and group ID
sudo mount /dev/sda1 /media/usb -o "uid=1000,gid=1000"

# Go into the server's repo
cd $server

# Pull from the mounted repository
git pull

# Go back
cd ..

# Go into the node's repo
cd $node

# Pull from the mounted repository
git pull

# Umount the USB
sudo umount /dev/sda1

# Go back
cd /
