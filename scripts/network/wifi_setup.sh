#!/bin/sh

sleep 5

insmod /usr/lib/modules/aic_load_fw.ko
sleep 3
insmod /usr/lib/modules/aic8800_fdrv.ko
sleep 5

wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant.conf
sleep 1

udhcpc -i wlan0 &
sleep 1
