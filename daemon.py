#!/usr/bin/python

import sys,os

class Daemon():
    def __init__(self):
        self.pid_file='/var/run/hbimserver.pid'
    def initDaemon(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
            sys.exit(1)
    
        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
            sys.exit(1)
        with open(self.pid_file,'w') as pid_file:
            pid_file.write('%d' % os.getpid())
