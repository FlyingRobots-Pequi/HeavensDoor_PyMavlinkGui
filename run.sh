#!/bin/bash

xhost +local:docker

docker run --rm \
  --privileged \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --name pid-calibrator \
  uopb_pid:1.0
