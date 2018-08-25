#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
from mininet.node import Controller, Rump
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
setLogLevel('info')

net = Mininet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')
info('*** Adding rumprun\n')
r1 = net.addHost('r1', ip='10.0.0.251', cls=Rump, rimage='~/img')
r2 = net.addRump('r2', ip='10.0.0.252', cls=Rump, rimage='~/img')
info('*** Adding a switch\n')
s1 = net.addSwitch('s1')
info('*** Creating links\n')
net.addLink(r1, s1)
net.addLink(s1, r2)
info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.ping([r1, r2])
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
