import webob
import webob.dec
import requests
import json
import config



class ImageAPI():
    def __init__(self):
        self.url="http://{}:{}".format(config.docker_host,config.docker_port)
    def get_images(self):
        headers={'Content-Type':'application/json'}
        result=requests.get("{}/images/json".format(self.url),headers=headers)	
        return result
    def get_image_by_id(self,image_id):
        headers={'Content-Type':'application/json'}
        result=requests.get("{}/images/json".format(self.url),headers=headers)
	return result
    def inspect_image(self,image_id):
	result=requests.get("{}/images/{}/json".format(self.url,image_id))
	return result
    def create_image(self):
	pass
    def delete_image(self,image_id):
        result=requests.delete("{}/images/{}".format(self.url,image_id))
        return result
		



class ImageController(object):
	@webob.dec.wsgify
	def __call__(self,request):
		method=request.environ['wsgiorg.routing_args'][1]['action']
		method=getattr(self,method)		
		response=webob.Response()
		result_json=method(request)
		response.json=result_json
		return response
	def __init__(self):
		self.image_api=ImageAPI()
	def index(self,request):
		result_json={}
		result=self.image_api.get_images()
		if result.status_code == 200:
			result_json=result.json()
		return result_json
	def show(self,request):
		result_json={}
		image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
		result = self.image_api.get_image_by_id(image_id)
		if result.status_code == 200:
			for res in result.json():
				if image_id in res['Id']:
					result_json = res	
		return result_json
	def inspect(self,request):
		image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
		result = self.image_api.inspect_image(image_id)
		result_json={}
		if result.status_code == 200:
			result_json=result.json()	
		if result.status_code == 404:
			errors={"errors":"404 Not Found:no such image {}".format(image_id)}
			result_json=errors
		return result_json
	def create(self,request):
		response.body="{create}\n"	
	def delete(self,request):
		image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
        	result=self.image_api.delete_image(image_id)
		if result.status_code == 200:
			result_json = result.json()	
		if result.status_code == 404:
			errors={"errors":"404 Not Found:no such image {}".format(image_id)}
			result_json=errors
		if result.status_code == 409:
			errors={"errors":"409 conflict"}
			result_json=errors
		if result.status_code == 500:
			errors={"errors":"500 internal server error"}
			result_json=errors
		return result_json

def create_resource():
	return ImageController()
