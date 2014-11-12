import threadgroup
import os
import wsgi
import log
import eventlet
import time
import signal
import config
import logging

LOG = logging.getLogger('eventlet.wsgi.server')

class WSGIService(object):
    def __init__(self):
        self.loader = wsgi.Loader()
        self.app = self.loader.load_app('api')
        self.host = '0.0.0.0'
        self.port = 8282 
        self.workers = 5 
        self.server = wsgi.Server(
                    self.app,
        	    self.host,
        	    self.port)
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
        self.children = {}
        rfd,self.writepipe = os.pipe()
        self.running = True

        signal.signal(signal.SIGTERM,self._handle_signal)
        signal.signal(signal.SIGINT,self._handle_signal)

    def _handle_signal(self,signo,frame):
	LOG.debug("master recived SIGTERM or SIGNIT...")
        self.running = False

    def _child_process(self,server):
        eventlet.hubs.use_hub()
		
        os.close(self.writepipe)

	signal.signal(signal.SIGTERM,signal.SIG_DFL)
	signal.signal(signal.SIGINT,signal.SIG_IGN)

        launcher = Launcher()
        launcher.run_service(server)

    def _start_child(self,wrap):
        pid = os.fork()
        if pid == 0:
            try:
                self._child_process(wrap.server)
            finally:
                wrap.server.stop()
            os._exit(0)
        wrap.children.add(pid)
        self.children[pid]=wrap

    def _wait_child(self):
	LOG.debug("wait for child...")
        pid,status = os.wait()
	LOG.debug(pid)
        if pid not in self.children:
            return None
        wrap = self.children.pop(pid)
        wrap.children.remove(pid)
        return wrap
		
    def launch_server(self,server,workers=1):
        wrap = ServerWrapper(server,workers)
        while len(wrap.children) < wrap.workers:
            self._start_child(wrap)

    def wait(self):
        while self.running: 
	    LOG.debug("master is running...")
            wrap = self._wait_child()
	    LOG.debug(wrap)
            if not wrap:
                continue
            while len(wrap.children) < wrap.workers:
                self._start_child(wrap)

	LOG.debug("master is going to die,kill workers first...")
        for pid in self.children:
            os.kill(pid,signal.SIGTERM)

        while self.children:
            self._wait_child()
