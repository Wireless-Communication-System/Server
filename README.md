# Wireless Communication System Server

Used by the stage manager to send cue updates to nodes

## Hardware

- Raspberry Pi 4
- Monitor
- Mouse
- Keyboard
- Power and display cables

## Dependencies

You will need to install the following dependencies via the following commands:

```bash
sudo apt-get install python3-pandas
sudo apt-get install python3-pyqt5
sudo apt-get install xterm -y
```

## Enabling/Disabling WiFi

Enabling:

```bash
sudo update-rc.d dhcpcd enable
sudo systemctl unmask wpa_supplicant.service
bash service wpa_supplicant start
```

Disabling:

```bash
bash service wpa_supplicant stop
sudo systemctl mask wpa_supplicant.service
sudo update-rc.d dhcpcd disable
```

## Setup of Code

1. Make the usb directory:

    ```bash
    sudo mkdir /media/usb
    ```

2. Plug in the USB flash drive
3. Mount the USB:

    ```bash
    uid='id -u'
    gid='id -g'
    sudo mount -o "uid=$uid,gid=$gid" /dev/sda1 /media/usb
    ```

4. Clone both the server and the node repositories off the USB flash drive and create the required folders:

    ```bash
    server="Server"
    node="Node"
    git clone /media/usb/USB/Update/$server
    git clone /media/usb/USB/Update/$node
    mkdir $server/Sent
    mkdir $server/Data
    mkdir $node/Sent
    ```

5. Unmount the USB flash drive:

    ```bash
    sudo umount /dev/sda1
    ```

6. Make the program start on startup

    1. Create an autostart directory:

        ```bash
        mkdir /home/pi/.config/autostart
        ```

    2. Copy the run_gui.desktop file from the repository to the autostart directory:

        ```bash
        desktopFile="run_server.desktop"
        sudo cp /home/pi/$repo/$desktopFile /home/pi/.config/autostart/$desktopFile
        ```

    3. Reboot to test: the GUI should start immediately when the desktop starts

        ```bash
        sudo reboot
        ```
