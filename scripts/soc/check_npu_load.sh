#!/use/bin/env bash

# npu load for RK3588
watch -n 1 cat /sys/kernel/debug/rknpu/load
