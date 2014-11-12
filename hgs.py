import webob
import webob.dec
import requests
import json
import config
from database import DBAPI
from utils import MercurialControl
import os
import utils
import time



class UserAPI():
    def __init__(self):
        self.url="http://{}:{}".format(config.docker_host,config.docker_port)
        self.db_api = DBAPI()
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
    def create_user(self,user_name,cn_name,department,email):
        result = {} 
        return result
    def delete_image(self,image_id):
        result=requests.delete("{}/images/{}".format(self.url,image_id))
        return result
        



class HgController(object):
    @webob.dec.wsgify
    def __call__(self,request):
        method=request.environ['wsgiorg.routing_args'][1]['action']
        method=getattr(self,method)     
        response=webob.Response()
        result_json=method(request)
        response.json=result_json
        return response
    def __init__(self):
        self.user_api=UserAPI()
        self.db_api=DBAPI()
    def index(self,request):
        result_json=[]
        project_id = request.GET.get('project_id')
        rs = self.db_api.get_hgs(project_id=project_id)
        for item in rs.fetchall():
            hg={
                'Id':item[0],
                'Content':item[1],
                'Created':item[3],
                }
            result_json.append(hg)
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
        project_id=request.json.pop('project_id')
        hg_addr=request.json.pop('hg_addr')
        created=utils.human_readable_time(time.time()) 
        self.db_api.add_hg(
                project_id = project_id,
                hg_addr = hg_addr,
                created = created,
        )
        result_json = {"status":200}
        return result_json
    def delete(self,request):
        hg_id=request.environ['wsgiorg.routing_args'][1]['id']
        self.db_api.delete_hg(hg_id)
        result='{"status":200}'
        return result

def create_resource():
    return ImageController()


