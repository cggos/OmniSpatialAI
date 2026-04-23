#!/bin/bash
### BEGIN INIT INFO
# Provides:          Gavin Gao
# Required-start:    $local_fs $remote_fs $network $syslog
# Required-Stop:     $local_fs $remote_fs $network $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: SAI Obstacle Dectection Script
# Description:
### END INIT INFO

/opt/scripts/sai_vod.sh
