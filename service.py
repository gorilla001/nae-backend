import threadgroup
import os
import wsgi
import log
import eventlet

class WSGIService(object):
    def __init__(self):
        self.loader = wsgi.Loader()
        self.app = self.loader.load_app('api')
        self.host = '0.0.0.0'
        self.port = 8282
        self.logger = log.getlogger()
        self.server = wsgi.Server(self.app,
				self.host,
				self.port,
				self.logger)
    def start(self):
	self.server.start()

    def wait(self):
	self.server.wait()
				
    

class ProcessLauncher(object):
    def __init__(self):
	self._services=[]
	self.children =set() 
	self.tg = threadgroup.ThreadGroup()

    @staticmethod
    def run_server(server):
	server.start()
	server.wait()	

    def _child_process(self,server):
	#gt=self.tg.start_thread(self.run_server,server)
	gt = eventlet.spawn(self.run_server, server)
	self._services.append(gt)

    def _start_child(self,server):
	pid = os.fork()
	if pid == 0:
	    self._child_process(server)
	self.children.add(pid)

    def launch_server(self,server,workers=1):
	while len(self.children) < workers:
	    self._start_child(server)

    def wait(self):
	for service in self._services:
	    service.wait()
