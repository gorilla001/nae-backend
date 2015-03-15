from netaddr import IPRange, IPAddress

from jae.common import cfg
from jae import db
from jae.base import Base
from jae.common import exception
from jae.common import log as logging
import subprocess

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

FIXED_RANGE = None


class NetworkManager(Base):
    def get_fixed_ip(self):
        global FIXED_RANGE
        if not FIXED_RANGE:
            FIXED_RANGE = self.get_fixed_range()

        query = self.db.get_networks()
        if query:
            for item in query:
                if item.fixed_ip:
                    if IPAddress(item.fixed_ip) in FIXED_RANGE:
                        FIXED_RANGE.remove(IPAddress(item.fixed_ip))

        for i in range(0,len(FIXED_RANGE)):
            ip_addr = str(FIXED_RANGE[i])
            if self.is_inuse(ip_addr):
                ip_addr = None
                continue
            break
        if not ip_addr:
            raise exception.NoValidIPAddress(msg='Ip resource has used up :(.')
        return ip_addr
        #try:
        #    return str(FIXED_RANGE[0])
        #except IndexError:
        #    raise exception.NoValidIPAddress(msg='Ip resource has used up :(.')

    def get_fixed_range(self):
        ip_resource_pool = CONF.ip_resource_pool
        if not ip_resource_pool:
            raise exception.NoValidIPAddress(msg="""Ip resource pool is None,
                                                  You must specified a ip resource range.""")

        start, _, end = ip_resource_pool.rpartition("-")

        ip_range = IPRange(start, end)

        return list(ip_range)

    def is_inuse(self,addr):
        try:
            LOG.info("Try to determine wether the ipaddr %s is in use..." % addr)
            subprocess.check_call("ping -c 3 %s" % addr, shell=True) 
        except subprocess.CalledProcessError:
            LOG.info("ipaddr %s not in use" % addr)
            return False 
        return True
