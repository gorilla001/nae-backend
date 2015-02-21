from jae.common import cfg
from jae.common import log as logging
from jae.common.rpc import kombu

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


def create_connection(new=True):
    """Create a new connection to the message bus""" 
    return kombu.create_connection(CONF,new=new)
