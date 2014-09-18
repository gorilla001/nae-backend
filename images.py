import webob
import webob.dec
import requests
import json
import config
from database import DBAPI



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
    def create_image_from_file(self,image_name,docker_file):
        headers={'Content-Type':'application/tar'}
        data={docker_file}
        result=requests.post("{}/images/build?t={}".format(self.url,image_name),headers=headers,data=json.dumps(data))
        return result
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
        self.db_api=DBAPI()
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
        image_name=request.json.pop('image_name')
        image_desc=request.json.pop('image_desc')
        docker_file=request.json.pop('docker_file')
        user_name=request.json.pop('user_name')

        print image_name,image_desc,docker_file,user_name
        #result=self.image_api.create_image_from_file(image_name,docker_file)
        #if result.status_code == 200:
        #    result_json=result.json()
        #if result.status_code == 500:
        #    errors={"errors":"500 internal server error"} 
        #    result_json=errors
        result_json={}
        return result_json
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
