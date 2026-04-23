#!/usr/bin/env bash

sudo mkdir /opt/scripts/
sudo cp scripts/upstart/sai_vod.sh /opt/scripts/

sudo chmod +x scripts/upstart/sai_vod_upstart.sh
sudo cp scripts/upstart/sai_vod_upstart.sh /etc/init.d/
sudo update-rc.d sai_vod_upstart.sh defaults 90
