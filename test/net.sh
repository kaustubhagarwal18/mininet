#!/bin/bash

export PATH=$PATH:~/work/ucl/unikernels/rumprun/rumprun/bin

ip tuntap add tap0 mode tap
ip addr add 10.0.0.10/24 dev tap0
ip link set dev tap0 up

rumprun qemu -i -M 128 \
       -I if,vioif,'-net tap,script=no,ifname=tap0'\
       -W if,inet,static,10.0.0.11/24 \
       -b ./data.iso,/data \
       -- ./nginx.rump -c /data/conf/nginx.conf

ip link delete tap0


