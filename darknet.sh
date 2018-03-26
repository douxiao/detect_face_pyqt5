#!/bin/bash
cd /home/dx/opt/darknet
./darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights
