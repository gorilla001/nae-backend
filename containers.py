import webob
import webob.dec
import requests
import json
import ast
#from database import DB
import config
from images import ImageAPI
import urllib
from pprint import pprint
import utils

class ContainerAPI():
    def __init__(self):
        self.url = "http://{}:{}".format(config.docker_host,config.docker_port) 
    def create_container(self,kargs,name):
	data = {
		'Hostname' : '',
		'User'	   : '',
		'Memory'   : '',
		'MemorySwap' : '',
		'AttachStdin' : False,
		'AttachStdout' : False,
		'AttachStderr': False,
		'PortSpecs' : [],
		'Tty'	: True,
		'OpenStdin' : True,
		'StdinOnce' : False,
		'Env' : None,
		'Cmd' : [], 
		'Dns' : None,
		'Image' : None,
		'Volumes' : {},
		'VolumesFrom' : '',
		'ExposedPorts': {},
	}
	data.update(kargs)
	pprint(data)
	headers={'Content-Type':'application/json'}
	resp = requests.post("{}/containers/create?name={}".format(self.url,name),data=json.dumps(data),headers=headers)
	return resp
    def delete_container(self,container_id):
	result=requests.delete("{}/containers/{}".format(self.url,container_id))	
	return result
    def get_containers(self):
	result=requests.get("{}/containers/json?all=1".format(self.url))	
	return result
    def get_container_by_id(self,container_id):
	result=requests.get("{}/containers/json?all=1".format(self.url))	
	response=webob.Response()
	for res in result.json():
		if container_id in res['Id']:
			#response.json = res	
			pass
	return result 
    def start_container(self,container_id,exposed_port):
	random_port=utils.get_random_port()
	data = {
		'Binds':[],
		'Links':[],
		'LxcConf':{},
		'PortBindings':{exposed_port:[{'HostPort':'{}'.format(random_port)}]},
		'PublishAllPorts':False,
		'Privileged':False,
		'Dns':[config.DNS],
		'VolumesFrom':[],
		'CapAdd':[],
		'CapDrop':[],
	}
	pprint(data)
	headers={"Content-Type":"application/json"}
	result=requests.post("{}/containers/{}/start".format(self.url,container_id),data=json.dumps(data),headers=headers)	
	return result
    def stop_container(self,container_id):
	result=requests.post("{}/containers/{}/stop?t=3".format(self.url,container_id))
	return result
    def kill_container(self,container_id):
	result=requests.post("{}/containers/{}/kill?signal=SIGINT".format(self.url,container_id))
	return result


class ContainerController(object):
    def __init__(self):
    	self.compute_api=ContainerAPI()
	self.image_api=ImageAPI()
    @webob.dec.wsgify
    def __call__(self,request):
	print request.environ['wsgiorg.routing_args']
	print request.method
    	method=request.environ['wsgiorg.routing_args'][1]['action']
	print '----------------'
	print method
	print '----------------'
    	method=getattr(self,method)		
    	response=webob.Response()
    	result_json=method(request)
    	response.headers.add("Content-Type","application/json")
    	response.json=result_json
    	return response
    def index(self,request):
    	containers=self.compute_api.get_containers()
    	return containers
    def show(self,request):
    	container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
    	container=self.compute_api.get_container_by_id(container_id)
    	return container
    def inspect(self,request):
    	container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
    	result=requests.get("http://0.0.0.0:2375/containers/{}/json".format(container_id))
    	#if result.status_code == 200:
    	#	response.json=json.dumps(dict(result.json()))
    	#if result.status_code == 404:
    	#	errors={"errors":"404 Not Found:no such container {}".format(container_id)}
    	#	response.json=errors
    	#	
    def delete(self,request):
	result_json={}
    	container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
	result=self.compute_api.kill_container(container_id)
	if result.status_code == 204:
		result_json = {"succeed":"{} stopped".format(container_id)}
	if result.status_code == 404:
		result_json = {"error":"404 no such container"}
		return result_json
	if result.status_code == 500:
		result_json = {"error":"500 server error"}
		return result_json
    	result=self.compute_api.delete_container(container_id)
	if result.status_code == 204:
		result_json = {"succeed":"{} deleted".format(container_id)}
	if result.status_code == 400:
		result_json = {"error":"400 bad parameter"}	
	if result.status_code == 404:
		result_json = {"error":"404 no such container"}
	if result.status_code == 500:
		result_json = {"error":"500 internal server error"}
    	return result_json
    def create(self,request):
	body=request.POST
	image=body.pop('Image')
	cmd=body.pop('Cmd')
	result = self.image_api.inspect_image(image)
	result_json={}
	if result.status_code == 200:
		result_json=result.json()	
	if result.status_code == 404:
		errors={"errors":"404 Not Found:no such image {}".format(image_id)}
		result_json=errors
		return result_json
	port=result_json['config']['ExposedPorts']
	name=request.params['name']
	kwargs={
		'Image':image,
		'Cmd':[cmd],
		'ExposedPorts':port,
	}
	resp=self.compute_api.create_container(kwargs,name)
	result_json={}
	if resp.status_code == 201:
		result_json = resp.json() 
		resp = self.compute_api.start_container(result_json['Id'],port.keys()[0])
		if resp.status_code == 204:
			result_json={"succeed":"start ok"}
		if resp.status_code == 304:
			result_json={"error":"304 container already started"}
		if resp.status_code == 404:
			result_json={"error":"404 no such container"}
		if resp.status_code == 500:
			result_json={"error":"500 server error"}	
	if resp.status_code == 404:
		result_json = {"error":"404 no such image:{}".format(Image)}
	if resp.status_code == 406:
		result_json = {"error":"impossible to attach(container not running)"}	
	if resp.status_code == 409:
		result_json = {"error":"409 Conflict, The name memcached6 is already assigned"}
	if resp.status_code == 500:
		result_json = {"error":"500 server error"}
	return result_json
    	#if 'name' not in container_dict:
    	#	msg = _("Container name is not defined")
    	#	raise exc.HTTPBadRequest(explanation=msg)
    
    	#image_id=self._image_from_req_data(body)
    	#
    	#command_context=self._command_from_req_data(body)
    
    	#exposed_port=self._get_exposed_port(image_id)
    
    	#self.compute_api.create_container(name,image_id,exposed_port,command_context)
    	#params=list(request.POST)[0]
    	#params_dict=ast.literal_eval(params)
    	#cmd=params_dict.get('cmd')
    	#image=params_dict.get('image')	
    	#args={'Cmd':cmd,'Image':image}	
    	#url="http://0.0.0.0:2375/container/create"
    	#headers={'Content-Type':'application/json'}
    	#result=requests.post(url,data=json.dumps(args),headers=headers)
    	#print result.status_code
    	#if result.status_code == 404:
    	#	error={"error":"404 Not Found:no such image {}".format(image)}
    	#	response.json=error
    	#if result.status_code == 201:
    	#	response.json=json.dumps(dict(result.json()))
    	#if result.status_code == 500:
    	#	error={"error":"500 internal server error"}
    	#	response.json=error
    		
