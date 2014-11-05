import threadgroup
import os
import wsgi
import log
import eventlet
import time
import signal
import config

class WSGIService(object):
	def __init__(self):
		self.loader = wsgi.Loader()
		self.app = self.loader.load_app('api')
		self.host = '0.0.0.0'
		self.port = config.port
        self.logger = log.getlogger()
        self.workers = config.workers
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
        self.children = {}
        rfd,self.writepipe = os.pipe()
        self.running = True

        signal.signal(signal.SIGTERM,self._handle_signal)
        signal.signal(signal.SIGINT,self._handle_signal)

    def _handle_signal(self,signo,frame):
        self.running = False

    def _child_process(self,server):
        eventlet.hubs.use_hub()
		
        os.close(self.writepipe)

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
        pid,status = os.wait()
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
            wrap = self._wait_child()
            if not wrap:
                continue
            while len(wrap.children) < wrap.workers:
                self._start_child(wrap)
        for pid in self.children:
            os.kill(pid,signal.SIGTERM)

        while self.children:
            self._wait_child()
