#!/bin/bash

rumprun qemu -M 128 -i \
             -b data.iso,/data \
             -- nginx.rump -c /data/conf/nginx.conf
