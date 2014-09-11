import webob
import webob.dec
import requests
import json

class MiscAPI():
	def get_system_info(self):
	    headers={'Content-Type':'application/json'}
	    result=requests.get("http://0.0.0.0:2375/info",headers=headers)	
	    return result
	def get_docker_version(self):
	    headers={'Content-Type':'application/json'}
	    result=requests.get("http://0.0.0.0:2375/version",headers=headers)
	    return result
	def get_docker_events(self):
	    headers={'Content-Type':'application/json'}
	    result=requests.get("http://0.0.0.0:2375/events",headers=headers)
	    return result



class MiscController(object):
	@webob.dec.wsgify
	def __call__(self,request):
		method=request.environ['wsgiorg.routing_args'][1]['action']
		method=getattr(self,method)		
		response=webob.Response()
		result=method(request)
		response.json=result.json()
		return response
	def __init__(self):
		self.misc_api=MiscAPI()
	def info(self,request):
		system_info=self.misc_api.get_system_info()
		return system_info 
	def version(self,request):
		version = self.misc_api.get_docker_version()
		return version 
	def events(self,request):
		events = self.misc_api.get_docker_events()
		return events 

def create_resource():
	return Controller()
