import webob

class Application(object):
	pass

class Resource(object):
	def __init__(self,controller):
		self.controller = controller
	@webob.dec.wsgify
	def __call__(self,request):
		action_args = self.get_action_args(request.environ)
		action = action_args.pop('action',None)
		content_type,body = self.get_body(request)
		accept='application/json'
		return self._process_stack(request,action,action_args,content_type,body,accept)
	def get_action_args(self,request_environment):
		args = request_environment['wsgiorg.routing_args'][1].copy()

		try:
		    del args['controller']
		except	KeyError:
		    pass
		try:
		    del args['format']
		except KeyError:
		    pass

		return args	
	def get_body(self,request):
		content_type = request.get_content_type()
		return content_type,request.body

	def _process_stack(self,request,action,action_args,content_type,body,accept):
		method = self.get_method(request,action,content_type,body)
		action_result=self.dispatch(method,request,action_args)
		response = action_result
		return response

	def get_method(self,request,action,content_type,body):
		method=self._get_method(request,action,content_type,body)
	def _get_method(self,request,action,content_type,body):
		method=getattr(self.controller,action)
		return self.wsgi_actions[action_name] 
	def dispatch(self,method,request,action_args):
		method=getattr(self.controller,method)
		method(request,action_args)
