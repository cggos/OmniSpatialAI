
sudo docker run -t -i --privileged \
	-v /dev/bus/usb:/dev/bus/usb \
	-v /home/gavin/projects/ml/rk/:/sai_rknn_tk \
	rknn-toolkit2:1.6.0-cp38 /bin/bash

