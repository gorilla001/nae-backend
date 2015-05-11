import os
import subprocess

from jae.common import log as logging
from jae.common import cfg


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def maven_code(uuid, user_id, repos, maven_flags):
    root_war = maven_flags.split("-JM")[1]
    maven_flags = maven_flags.split("-JM")[0]
    path = CONF.base_data_dir
    if path is None:
        path = os.path.expandvars('$HOME')
    code_path = "%s/%s/%s/www/%s" % (path,user_id,uuid[:12],os.path.basename(repos))

    """Packaging..."""
    LOG.info("Begin packaging...")
    try:
        #subprocess.check_call("source /etc/profile",shell=True)
        LOG.info("/home/jm/maven/bin/mvn -f %s clean package %s" % (code_path,maven_flags))
        subprocess.check_call("source /etc/profile && /home/jm/maven/bin/mvn -f %s clean package %s" % (code_path,maven_flags),shell=True)
        LOG.info("Packaging succeed")
    except:
        LOG.error("maven packaging failed...skip")
        return

    new_root_war = "/home/jm/www/%s" % root_war 
    """Restart tomcat..."""
    try:
        """Get container's pid namespace"""
        LOG.info("Get container's namespace pid")
        pid = subprocess.check_output("sudo docker inspect --format '{{.State.Pid}}' %s" % uuid, shell=True)
        LOG.info("Pid is %s" % pid.strip())

        """Startup Service Init"""
        LOG.info("Service init...")

        LOG.info("/etc/init.d/tomcat stop")
        subprocess.check_call("sudo nsenter -t %s --mount -n --pid -- /etc/init.d/tomcat stop" % pid.strip(), shell=True)

        LOG.info("rm -rf /home/jm/tomcat/webapps")
        subprocess.check_call("sudo nsenter -t %s --mount -n --pid -- rm -rf /home/jm/tomcat/webapps" % pid.strip(), shell=True)

        LOG.info("mkdir /home/jm/tomcat/webapps")
        subprocess.check_call("sudo nsenter -t %s --mount -n --pid -- mkdir /home/jm/tomcat/webapps" % pid.strip(), shell=True)
   
        LOG.info("cp %s /home/jm/tomcat/webapps/ROOT.war" % new_root_war)
        subprocess.check_call("sudo nsenter -t %s --mount -n --pid -- cp %s /home/jm/tomcat/webapps/ROOT.war" % (pid.strip(),new_root_war), shell=True)

        LOG.info("chown -R tomcat:tomcat /home/jm/tomcat/webapps/")
        subprocess.check_call("sudo nsenter -t %s --mount -n --pid -- chown -R tomcat:tomcat /home/jm/tomcat/webapps/" % pid.strip(), shell=True)

        LOG.info("/etc/init.d/tomcat start")
        #subprocess.check_call("sudo nsenter -t %s --mount -n --pid -- /etc/init.d/tomcat start" % pid.strip(), shell=True)
        subprocess.check_call("sudo docker exec %s /etc/init.d/tomcat start" % uuid, shell=True)
        LOG.info("Start tomcat succeed")
    except subprocess.CalledProcessError as ex:
        LOG.error("Tomcat start failed...check it")
        LOG.error(ex)

def composer_code(uuid, user_id, repos):
    path = CONF.base_data_dir
    if path is None:
        path = os.path.expandvars('$HOME')
    code_path = "%s/%s/%s/www/%s" % (path,user_id,uuid[:12],os.path.basename(repos))
    origin_uid, origin_gid = os.stat(code_path).st_uid, os.stat(code_path).st_gid 
    try:
        LOG.info("Running %s" % ("cd %s && sudo /usr/local/bin/composer update -q" % code_path))
        subprocess.check_call("cd %s && sudo /usr/local/bin/composer update -q" % code_path, shell=True) 
        os.system("sudo chown -R %s:%s %s" % (origin_uid, origin_gid, code_path))
    except:
        LOG.error("Exec composer update -q failed...do it manually")

    
     
