import threadgroup
import os
import wsgi
import log
import eventlet
import time
import signal

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

    def stop(self):
	    self.server.stop()

    def wait(self):
	    self.server.wait()
				
class ServerWrapper(object):
    def __init__(self,server,workers):
	    self.server = server
	    self.workers = workers
	    self.children = set()    

class Launcher(object):
    @staticmethod
    def run_service(service):
        service.start()
        service.wait()

class ProcessLauncher(object):
    def __init__(self):
        self._services=[]
        self.tg = threadgroup.ThreadGroup()
        rfd,self.writepipe = os.pipe()

    def _child_process(self,server):
        eventlet.hubs.use_hub()
        
        os.close(self.writepipe)
        #gt=self.tg.start_thread(self.run_server,server)
        #gt = eventlet.spawn(self.run_server, server)
        #self._services.append(gt)
        #self.run_server(server)
        launcher = Launcher()
        launcher.run_service(server)

    def _start_child(self,wrap):
	    pid = os.fork()
	    if pid == 0:
	        self._child_process(wrap.server)
	        os._exit(0)
	    wrap.children.add(pid)

    def launch_server(self,server,workers=1):
	    wrap = ServerWrapper(server,workers)
	    while len(wrap.children) < wrap.workers:
	        self._start_child(wrap)

    def wait(self):
	    #for service in self._services:
	    #    service.wait()
        while True:
            time.sleep(5)
