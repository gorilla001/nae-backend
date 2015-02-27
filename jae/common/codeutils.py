import os
import subprocess

from jae.common import log as logging


LOG = logging.getLogger(__name__)


def maven_code(uuid, user_id, repos, maven_flags, root_war):
    code_path = "/home/jae/%s/%s/www/%s" % (user_id,uuid[:12],os.path.basename(repos))

    """Packaging..."""
    LOG.info("Begin packaging...")
    try:
        #subprocess.check_call("source /etc/profile",shell=True)
        subprocess.check_call("source /etc/profile && /home/jm/maven/bin/mvn -f %s clean package %s" % (code_path,maven_flags),shell=True)
        LOG.info("Packaging succeed")
    except:
        LOG.error("maven packaging failed...skip")
        return

    new_root_war = "/home/jm/www/%s/%s" % (os.path.basename(repos),root_war) 
    """Restart tomcat..."""
    try:
        """Get container's pid namespace"""
        LOG.info("Get container's namespace pid")
        pid = subprocess.check_output("sudo docker inspect --format '{{.State.Pid}}' %s" % uuid, shell=True)
        LOG.info("Pid is %s" % pid.strip())

        """Startup Service Init"""
        LOG.info("Init host")
        subprocess.check_call("sudo nsenter -t %s --mount -n --pid /etc/init.d/tomcat stop && rm -rf /home/jm/tomcat/webapps/* && cp %s /home/jm/tomcat/webapps/ROOT.war && chown -R tomcat:tomcat /home/jm/tomcat/webapps/ && /etc/init.d/tomcat start" % (pid.strip(),new_root_war), shell=True)
        LOG.info("Start tomcat succeed")
    except subprocess.CalledProcessError as ex:
        LOG.error("Tomcat start failed...check it")
        LOG.error(ex)

def composer_code(uuid, user_id, repos):
    code_path = "/home/jae/%s/%s/www/%s" % (user_id,uuid[:12],os.path.basename(repos))
    try:
        subprocess.check_call("cd %s && sudo /usr/local/bin/composer update -q" % code_path, shell=True) 
    except:
        LOG.error("Exec composer update -q failed...do it manually")

    
     
