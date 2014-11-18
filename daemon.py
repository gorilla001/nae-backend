#!/usr/bin/python

import sys,os

class Daemon():
    def __init__(self,stdout="/var/log/jaecpn/jaecpn.log",stderr="/var/log/jaecpn/jaecpn.log"):
        self.pid_file='jaecpn.pid'
    def initDaemon(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
            sys.exit(1)
    
        os.chdir(os.path.dirname(__file__))
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
            sys.exit(1)
	
	for f in sys.stdout,sys.stderr:
	    f.flush()
        so = file(stdout,'a+')
	se = file(stderr,'a+',0) 
	os.dup2(so.fileno(),sys.stdout.fileno())
	os.dup2(se.fileno(),sys.stderr.fileno())

        with open(self.pid_file,'w') as pid_file:
            pid_file.write('%d' % os.getpid())
