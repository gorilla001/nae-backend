import config
import random
import tarfile
import os

import mercurial.commands
import mercurial.ui
import mercurial.hg
import logging
from random import Random

import contextlib
import time
import stat
import pwd
import daemon

from database import DBAPI

def init():
    daemon.Daemon().initDaemon()
 
def get_random_port():
	port_range=config.PortRange.strip("'").split(':')	
	random_port = random.randint(int(port_range[0]),int(port_range[1]))
		
	return random_port

def random_str(randomlength=8):
    str = ''
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

def get_file_path(user_name,repo_name):
    base_dir = os.path.dirname(__file__)
    user_dir=os.path.join(base_dir,'files',user_name,repo_name)

    return user_dir 

def repo_exist(user_name,repo_name):
    base_dir=os.path.dirname(__file__)
    print base_dir,user_name
    user_dir=os.path.join(base_dir,'files',user_name)
    repo_dir=os.path.join(user_dir,repo_name)
    if not os.path.exists(repo_dir):
        return False 
    return True
def human_readable_size(size):
    import humanize

    return humanize.naturalsize(size)

def human_readable_time(timestamp):
    _localtime = time.localtime(timestamp)
    _time_format = "%Y-%m-%d %H:%M:%S"

    return time.strftime(_time_format,_localtime)

def create_user_access(user_name):
    user_home = make_user_home(user_name)
    os.system('useradd -d {} -s /bin/bash {}'.format(user_home,user_name))
    os.system('echo {} | passwd {} --stdin'.format(random_str(),user_name))

@contextlib.contextmanager
def cd_change(tmp_location):
        cd = os.getcwd()
        os.chdir(tmp_location)
        try:
            yield
        finally:
            os.chdir(cd)

def make_zip_tar(path):
    _str=random_str()
    tar = tarfile.open("/tmp/%s.tar.gz" % _str,"w:gz")
    with cd_change(path):
        for file in os.listdir(path):
            if file[0] == '.' :
                continue
            tar.add(file)
    tar.close()

    return "/tmp/%s.tar.gz" % _str
def make_user_home(user_name,user_key):
    path = os.path.join(os.path.dirname(__file__),'files')
    user_home = os.path.join(path,user_name)
    if not os.path.exists(user_home):
        os.mkdir(user_home)
        os.chmod(user_home,stat.S_IRWXU+stat.S_IRGRP+stat.S_IXGRP+stat.S_IROTH+stat.S_IXOTH)
        ssh_dir = os.path.join(user_home,'.ssh')
        os.mkdir(ssh_dir)
        authorized_keys_file = os.path.join(ssh_dir,'authorized_keys')
        with open(authorized_keys_file,'a') as f:
            f.write('{}\n'.format(user_key))
    return user_home

def change_dir_owner(home,user_name):
    uid = pwd.getpwnam(user_name).pw_uid
    gid = pwd.getpwnam(user_name).pw_gid
    os.system('chown -R {}:{} {}'.format(uid,gid,home))

def prepare_config_file(home,repo,env):
    path = os.path.join(home,repo)
    if env == 'config-dev':
        config_file = os.path.join(path,'config-dev')
        os.rename(config_file,os.path.join(path,'config'))
        

def get_projects(user_id):
    db=DBAPI()
    project_id=list()
    user_info= db.get_project_id_by_user_id(user_id)
    if user_info is not None:
        for item in user_info:
           _project_id = item[4] 
           project_id.append(_project_id)
    return project_id

def get_project_info(project_id):
    db=DBAPI()
    project_info = db.show_project(project_id)
    return project_info.fetchone()
def get_containers(project_id,user_id):
    db=DBAPI()
    return



class MercurialControl(object):
    def __init__(self):
        self._ui = mercurial.ui.ui()
        self.path=os.path.join(os.path.dirname(__file__),'files')
    def clone(self,user_name,repo_path):
        #source = 'ssh://localhost/%s' % repo_path
        source = repo_path
        path = os.path.join(self.path,user_name)
        dest = os.path.join(path,os.path.basename(repo_path)) 
        try:
            mercurial.commands.clone(self._ui,str(source),str(dest),pull=False,uncompressed=False,rev=False,noupdate=False)
            logging.debug('clone docker file from %s' % repo_path)
        except Exception,error:
            logging.error('could not clone repo:%s' % repo_path)
            logging.error(error)
    def pull(self,user_name,repo_path):
        #source = 'ssh://localhost/%s' % repo_path
        source = repo_path
        path = os.path.join(self.path,user_name)
        local_repo_path = os.path.join(path,os.path.basename(repo_path)) 
        repo=mercurial.hg.repository(self._ui,local_repo_path)
        mercurial.commands.pull(self._ui,repo,source=source)
    def update(self,user_name,repo_path,branch=None):
        path = os.path.join(self.path,user_name)
        local_repo_path = os.path.join(path,os.path.basename(repo_path)) 
        print 'local_repo_path',local_repo_path
        repo=mercurial.hg.repository(self._ui,local_repo_path)
        mercurial.commands.update(self._ui,repo,rev=branch,clean=True)


if __name__ == '__main__':
	print get_random_port()
