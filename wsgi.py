import webob
from eventlet import wsgi
import eventlet

#class Application(object):
#	pass
#
#class Resource(object):
#	def __init__(self,controller):
#		self.controller = controller
#	@webob.dec.wsgify
#	def __call__(self,request):
#		action_args = self.get_action_args(request.environ)
#		action = action_args.pop('action',None)
#		content_type,body = self.get_body(request)
#		accept='application/json'
#		return self._process_stack(request,action,action_args,content_type,body,accept)
#	def get_action_args(self,request_environment):
#		args = request_environment['wsgiorg.routing_args'][1].copy()
#
#		try:
#		    del args['controller']
#		except	KeyError:
#		    pass
#		try:
#		    del args['format']
#		except KeyError:
#		    pass
#
#		return args	
#	def get_body(self,request):
#		content_type = request.get_content_type()
#		return content_type,request.body
#
#	def _process_stack(self,request,action,action_args,content_type,body,accept):
#		method = self.get_method(request,action,content_type,body)
#		action_result=self.dispatch(method,request,action_args)
#		response = action_result
#		return response
#
#	def get_method(self,request,action,content_type,body):
#		method=self._get_method(request,action,content_type,body)
#	def _get_method(self,request,action,content_type,body):
#		method=getattr(self.controller,action)
#		return self.wsgi_actions[action_name] 
#	def dispatch(self,method,request,action_args):
#		method=getattr(self.controller,method)
#		method(request,action_args)
#
class Server(object):
	default_pool_size = 1000

	def __init__(self,app,host,port,logger,backlog=128):
	    self._server = None
	    self._protocol = eventlet.wsgi.HttpProtocol
	    self.pool_size = self.default_pool_size
	    self._pool=eventlet.GreenPool(self.pool_size)
	    self._logger=logger
	    self._wsgi_logger=logging.WritableLogger(self._logger)
	    
	    bind_addr = (host,port)
	    self._socket=eventlet.listen(bind_addr,family=2,backlog=backlog)
	def start(self):
	    dup_socket = self._socket.dup()
	    wsgi_kwargs = {
            		'func': eventlet.wsgi.server,
            		'sock': dup_socket,
            		'site': self.app,
            		'protocol': self._protocol,
            		'custom_pool': self._pool,
            		'log': self._wsgi_logger,
            		'debug': False
            		}
	    self._server = eventlet.spawn(**wsgi_kwargs)
	def wait(self):
	    self._pool.waitall()
	    self._server.wait()

#class Loader(object):
#	def __init__(self,config_path):
#		self.config_path=config_path
#	def load_app(self,name):
#		return deploy.loadapp("config:%s" % self.config_path,name=name)
#
#class WSGIService(object):
#	def __init__(self,name):
#		self.name = name
#		self.loader = Loader()
		
