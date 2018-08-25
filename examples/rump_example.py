#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
import os
from mininet.node import Controller, Rump
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
setLogLevel('info')

net = Mininet(controller=Controller)

info('*** Adding controller...\n')
net.addController('c0')

info('*** Adding a switches...\n')
s1 = net.addSwitch('s1')

info('*** Adding rumprun host...\n')
r1 = net.addHost('r1',
  ip='10.0.0.1',
  rip='10.0.0.1',
  cls=Rump,
  rplatform='qemu',
  rmem=128,
  rcpu=1,
  rimage=os.getcwd() + '/test/nginx.rump',
  rargs='-b ' + os.getcwd() + '/test/data.iso,/data',
  iargs='-c /data/conf/nginx.conf')

r2 = net.addHost('r2',
  ip='10.0.0.2',
  rip='10.0.0.2',
  cls=Rump,
  rplatform='qemu',
  rmem=128,
  rcpu=1,
  rimage=os.getcwd() + '/test/nginx.rump',
  rargs='-b ' + os.getcwd() + '/test/data.iso,/data',
  iargs='-c /data/conf/nginx.conf')

info('*** Creating links...\n')
net.addLink(s1, r1)
net.addLink(s1, r2)

info('*** Starting network\n')
net.start()

info('*** Testing connectivity\n')
net.ping([s1, r2])

info('*** Running CLI\n')

CLI(net)

info('*** Stopping network')

net.stop()
