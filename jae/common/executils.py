import subprocess
from jae.common import log as logging 


LOG=logging.getLogger(__name__)


def inject_key(uuid, key):
    """Inject public key into container"""

    """Get container's pid namespace"""
    LOG.info("Get container's namespace pid")
    pid = subprocess.check_output("sudo docker inspect --format '{{.State.Pid}}' %s" % uuid, shell=True)
    LOG.info("Pid is %s" % pid.strip())

    try:
        LOG.info("Inject public key into container")
        subprocess.check_call("sudo nsenter -t %s --mount echo %s >> /root/.ssh/authorized_keys" % (pid.strip(), key), shell=True)
    except subprocess.CalledProcessError:
        LOG.error("Falied")
