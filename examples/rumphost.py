#!/usr/bin/env python
"""
rumphost.py: Host subclass that uses a Rumprun unikernels.

Dependencies:
    TODO

Usage:
    TODO
"""

from mininet.node import Host
from mininet.util import quietRun
from mininet.log import error, debug
from subprocess import call, Popen, PIPE, STDOUT

"""
Node that represents a rumprun unikernel.
"""
class RUMPHost( Host ):

    # Supported platforms by Rump
    _platforms = ["ec2", "iso", "kvm", "qemu", "xen"]

    #
    # Rump unikernel constructor
    #
    # @param platform The platform the unikernel intends to run
    # @param mem The amount of allocated RAM for the instance
    # @param cpu The amount of cores allocated to the isntance
    # @param image The binary image specified for the platform
    # @param extra Additional rumprun commands for the instantiation command
    # @param cmd Commandline parameters for the instance on initialization (image-specific)
    #
    def __init__(self, name, platform='qemu', mem=128, cpu=1, image=None, extra=None, cmd=None, **params):
        if platform not in self._platforms:
            error("Specified hypervisor platform not supported!")

        # self.conn = libvirt.openReadOnly(None)
        # if conn == None:
        #     print 'Failed to open connection to the hypervisor'
        #     sys.exit(1)
        
        self.platform = platform
        self.mem = mem
        self.cpu = cpu
        self.image = image
        self.extra = extra
        self.cmd = cmd
        self.ip = params['ip'] # Retrieved from net.addHost

        super( RUMPHost, self ).__init__( name, **params )
  
    #
    # Initialize the unikernel image
    #
    def startShell(self, *args, **kwargs):
        "Initialize the rumpkernel VM"
        if self.shell:
            error('This particular rump unikernel has already been initialized!')
            return

        initcmd = 'rumprun ' + self.platform + ' -M ' + str(self.mem) + ' -i ' + ' -I if,vioif,"-net tap,script=no,ifname=s1-eth1@r1-eth1" ' + ' -W if,inet,static,' + self.ip + ' ' + self.extra + ' -- ' + self.image + ' ' + self.cmd

        print(initcmd)

        self.shell = self._popen(initcmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT) # , close_fds=True )
        
        self.stdin = self.shell.stdin
        self.stdout = self.shell.stdout
        self.pid = self.shell.pid

        # Maintain mapping between file descriptors and nodes
        # This is useful for monitoring multiple nodes
        # using select.poll()
        self.outToNode[ self.stdout.fileno() ] = self
        self.inToNode[ self.stdin.fileno() ] = self
        self.execed = False
        self.lastCmd = None
        self.lastPid = None
        self.readbuf = ''
        self.waiting = False

    def sendCmd(self, *args, **kwargs):
        return False

    def popen(self, *args, **kwargs):
        pass

    def terminate(self ):
        termcmd = 'rumpstop'

    def cmd(self, *args, **kwargs):
        pass
    
    def config(self, **params):
        """Configure RUMPHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super(RUMPHost, self).config(**params)

        intf = self.defaultIntf()

        # Create tap interface
        self.cmd('ip tuntap add %s mode tap' % intf)
        
        # Assign IP address to said tap interface
        self.cmd('ip addr add %s/24 dev %s' % (params['ip'], intf))

        # Bring tap interface up
        self.cmd('ip link set dev %s up' % intf)

        return r

if __name__ == '__main__':
    import sys, os
    from functools import partial
    from mininet.node import Controller
    from mininet.cli import CLI
    from mininet.link import TCLink
    from mininet.log import info, setLogLevel
    from mininet.net import Mininet

    setLogLevel( 'info' )

    if not quietRun( 'which rumprun' ):
        error("Cannot find command 'rumprun'!\n"
              "This tool is required before continuing!\n\n"
              "Learn more at: https://github.com/rumpkernel/rumprun" )
        exit()

    net = Mininet(controller=Controller)
    net.addController('c0')
    s1 = net.addSwitch('s1')

    r1 = net.addHost('r1',
      cls=RUMPHost,
      #platform='qemu',
      mem=128,
      cpu=1,
      image=os.getcwd() + '/test/nginx.rump',
      extra='-b ' + os.getcwd() + '/test/data.iso,/data',
      cmd='-c /data/conf/nginx.conf'
    )

    # r2 = net.addHost('r2',
    #   ip='10.0.0.2',
    #   cls=RUMPHost,
    #   platform='qemu',
    #   mem=128,
    #   cpu=1,
    #   image=os.getcwd() + '/test/nginx.rump',
    #   extra='-b ' + os.getcwd() + '/test/data.iso,/data',
    #   cmd='-c /data/conf/nginx.conf')

    info('*** Creating links...\n')
    net.addLink(s1, r1)
    # net.addLink(s1, r2)

    info('*** Starting network\n')
    net.start()

    info('*** Testing connectivity\n')
    # net.ping([s1, r2])

    info('*** Running CLI\n')

    # CLI(net)

    info('*** Stopping network')

    net.stop()
