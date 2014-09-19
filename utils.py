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

def get_random_port():
	port_range=config.PortRange.strip("'").split(':')	
	random_port = random.randint(int(port_range[0]),int(port_range[1]))
		
	return random_port

def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

def get_file_path(file_name):
    base_dir = os.path.dirname(__file__)

    return os.path.join(base_dir,'files',file_name)

def repo_exist(repo_name):
    base_dir=os.path.dirname(__file__)
    repo_dir=os.path.join(base_dir,'files',repo_name)
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

class MercurialControl(object):
    def __init__(self):
        self._ui = mercurial.ui.ui()
        self.path=os.path.join(os.path.dirname(__file__),'files')
    def clone(self,repo_path):
        source = 'ssh://localhost/%s' % repo_path
        dest = os.path.join(self.path,os.path.basename(repo_path)) 
        try:
            mercurial.commands.clone(self._ui,str(source),str(dest),pull=False,uncompressed=False,rev=False,noupdate=False)
            logging.debug('clone docker file from %s' % repo_path)
        except Exception,error:
            logging.error('could not clone repo:%s' % repo_path)
            logging.error(error)
    def pull(self,repo_path):
        source = 'ssh://localhost/%s' % repo_path
        repo=mercurial.hg.repository(self._ui,repo_path)
        mercurial.commands.pull(self._ui,repo,source=source)


if __name__ == '__main__':
	print get_random_port()
