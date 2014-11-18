#!/usr/bin/python

import sys,os
import logging

LOG=logging.getLogger('eventlet.wsgi.server')

class Daemon():
    def __init__(self):
        self.pid_file='jaecpn.pid'
	self.stdout="/var/log/jaecpn/jaecpn.log"
	self.stderr="/var/log/jaecpn/jaecpn.log"
    def initDaemon(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
	    LOG.error("fork error")
            sys.exit(1)
    
        os.chdir(os.path.dirname(__file__))
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
	    LOG.error("fork error")
            sys.exit(1)
	
	for f in sys.stdout,sys.stderr:
	    f.flush()
        so = file(self.stdout,'a+')
	se = file(self.stderr,'a+',0) 
	os.dup2(so.fileno(),sys.stdout.fileno())
	os.dup2(se.fileno(),sys.stderr.fileno())

        with open(self.pid_file,'w') as pid_file:
            pid_file.write('%d' % os.getpid())
