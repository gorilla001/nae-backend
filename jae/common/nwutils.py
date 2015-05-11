# import commands
from jae.common import cfg
from jae.common import log as logging
from jae.common import cmdutils
from jae.common.exception import NetWorkError
import os
import subprocess

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

#TEMP_PATH="/tmp"

#NET_SCRIPT_PATH="/etc/sysconfig/network-scripts/"

DEFAULT_NET_MASK = "255.255.255.0"

def get_default_gateway():
    gateway = CONF.gateway
    if not gateway:
        import netifaces
        gws=netifaces.gateways()
        return gws['default'][netifaces.AF_INET][0]

    return gateway


def set_fixed_ip(uuid, addr):
    """Inject fixed ip to container instance.This method is similar to `pipework`
       but more simple.
       Generally contains the following four step:
           - create veth pair, one is external and the other is internal.
             >>ip link add web-int type veth peer name web-ext
           - add external veth to bridge `br0`.
             >>brctl addif br0 web-ext
           - add internal veth to container and rename to `eth1`.
             >>ip link set netns {{PID}} dev web-int
             >>nsenter -t {{PID}} -n ip link set web-int name eth1
           - add fixed ip addr for container's internal veth `eth1`.
             >>nsenter -t {{PID}} -n ip addr add ipaddr/netmask dev eth1
       You can also use dhcp for container ip allocated,as:
           >>nsenter -t {{PID}} -n -- dhclient -d eth1
    """

    if len(uuid) > 8:
        uuid = uuid[:8]

    uuid_reverse = uuid[::-1]
    veth_int = "%s%s" % ("veth", uuid_reverse)
    veth_ext = "%s%s" % ("veth", uuid)

    try:
        """First create veth pair: web-int and vethuuid"""
        LOG.info("Create veth pair: %s and %s" % (veth_int, veth_ext))
        cmdutils.run_command("sudo ip link add %s type veth peer name %s" % (veth_int, veth_ext))

        """Second add external veth to bridge `br0`"""
        LOG.info("Attach external veth %s to bridge `br0`" % veth_ext)
        cmdutils.run_command("sudo brctl addif br0 %s" % veth_ext)

        """Get container's pid namespace"""
        LOG.info("Get container's namespace pid")
        #pid = subprocess.check_output("sudo docker inspect --format '{{.State.Pid}}' %s" % uuid, shell=True)
        pid = cmdutils.call("sudo docker inspect --format '{{.State.Pid}}' %s" % (uuid,))
        LOG.info("Pid is %s" % pid.strip())

        """Add internal veth web-int to container"""
        LOG.info("Attach internal %s to container" % veth_int)
        #subprocess.check_call("sudo ip link set netns %s dev %s" % (pid.strip(), veth_int), shell=True)
        cmdutils.run_command("sudo ip link set netns %s dev %s" % (pid.strip(), veth_int))

        """Rename internal veth web-int to eth0"""
        LOG.info("Rename internal veth %s to eth0" % veth_int)
        #subprocess.check_call("sudo nsenter -t %s -n ip link set %s name eth0" % (pid.strip(), veth_int), shell=True)
        cmdutils.cast("sudo nsenter -t %s -n ip link set %s name eth0" % (pid.strip(), veth_int))
        #subprocess.check_call("sudo docker exec --cap-add=NET_ADMIN %s ip link set %s name eth0" % (uuid,veth_int), shell=True)

        """Set internal veth to UP"""
        LOG.info("UP internal veth eth0")
        #subprocess.check_call("sudo nsenter -t %s -n ip link set eth0 up" % pid.strip(), shell=True)
        cmdutils.cast("sudo nsenter -t %s -n ip link set eth0 up" % (pid.strip(),))
        #subprocess.check_call("sudo docker exec  %s ip link set eth0 up" % (uuid,), shell=True)

        """Set external veth to UP"""
        LOG.info("UP external %s" % veth_ext)
        #subprocess.check_call("sudo ip link set %s up" % veth_ext, shell=True)
        cmdutils.cast("sudo ip link set %s up" % (veth_ext,))

        """Set fixed ip to internal veth `eth0`"""
        IP_ADDR = "%s/%s" % (addr, DEFAULT_NET_MASK)

        LOG.info("Attach fixed IP to internal veth eth0")
        #subprocess.check_call("sudo nsenter -t %s -n ip addr add %s dev eth0" % (pid.strip(), IP_ADDR), shell=True)
        cmdutils.cast("sudo nsenter -t %s -n ip addr add %s dev eth0" % (pid.strip(), IP_ADDR))
        #subprocess.check_call("sudo docker exec  %s ip addr add %s dev eth0" % (uuid, IP_ADDR), shell=True)

        """Set default gateway to br0's gateway"""
        DEFAULT_GATEWAY = get_default_gateway()
        LOG.info("Set default gateway to %s" % DEFAULT_GATEWAY)
        #subprocess.check_call("sudo nsenter -t %s -n ip route del default" % pid.strip(),shell=True)
        #subprocess.check_call(
        #    "sudo nsenter -t %s -n ip route add default via %s dev eth0" % (pid.strip(), DEFAULT_GATEWAY), shell=True)
        cmdutils.cast("sudo nsenter -t %s -n ip route add default via %s dev eth0" % (pid.strip(), DEFAULT_GATEWAY))
        #subprocess.check_call(
        #    "sudo docker exec  %s ip route add default via %s dev eth0" % (uuid, DEFAULT_GATEWAY), shell=True)


        #"""Flush gateway's arp caching"""
        #LOG.info("Flush gateway's arp caching")
        #subprocess.check_call("sudo nsenter -t %s -n -- arping -c 1 -s %s %s" % (pid.strip(),addr,DEFAULT_GATEWAY),shell=True)

        """Ping gateway"""
        LOG.info("Flush gateway's arp caching")
        #subprocess.check_call("sudo nsenter -t %s -n ping -c 3 %s" % (pid.strip(), DEFAULT_GATEWAY), shell=True)
        #subprocess.check_call("sudo docker exec  %s ping -c 3 %s" % (uuid, DEFAULT_GATEWAY), shell=True)
        cmdutils.cast("sudo nsenter -t %s -n ping -c 3 %s" % (pid.strip(), DEFAULT_GATEWAY))

    except subprocess.CalledProcessError:
        raise

def service_init(uuid, user_id, repos):
    """This method is used for service init"""
    try: 
        LOG.info("Start maven packaging...")
        root_path = "/home/jae/%s/%s/www/%s" % (user_id, uuid[:12], os.path.basename(repos)) 
        #subprocess.check_call("sudo" )
        cmdutils.cast("sudo")
    except subprocess.CalledProcessError:
        """Reraise the exception, the caller will catch it"""
        raise

def host_init(uuid):
    try:
        """Get container's pid namespace"""
        LOG.info("Get container's namespace pid")
        #pid = subprocess.check_output("sudo docker inspect --format '{{.State.Pid}}' %s" % uuid, shell=True)
        pid = cmdutils.call("sudo docker inspect --format '{{.State.Pid}}' %s" % (uuid,))
        LOG.info("Pid is %s" % pid.strip())

        """Startup Host Init"""
        LOG.info("Init host")
        #subprocess.check_call("sudo docker exec %s /usr/local/bin/host.init" % uuid, shell=True)
        cmdutils.cast("sudo docker exec %s /usr/local/bin/host.init" % (uuid,))
    except subprocess.CalledProcessError:
        """Raise the exception, the caller will be catch it"""
        raise


def delete_virtual_interface(uuid):
    """This method contains the following two steps:
       1. Delete interface from bridge
       2. Delete interface thorough
    """
    if len(uuid) > 8:
        uuid = uuid[:8]
    veth_ext = "%s%s" % ("veth", uuid)

    try:
        LOG.info("Delete interface %s from bridge br0" % veth_ext)
        #subprocess.check_call("sudo brctl delif br0 %s" % veth_ext, shell=True)
        cmdutils.cast("sudo brctl delif br0 %s" % (veth_ext,))

        LOG.info("Delete interface %s" % veth_ext)
        #subprocess.check_call("sudo ip link del %s" % veth_ext, shell=True)
        cmdutils.cast(""sudo ip link del %s" % (veth_ext,))
    except subprocess.CalledProcessError:
        raise
