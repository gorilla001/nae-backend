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
        



class UserController(object):
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
        rs = self.db_api.get_users()
        for item in rs.fetchall():
            user={
                'UserId':item[0],
                'UserName':item[1],
                'CNName':item[2],
                'DepartMent':item[3],
                'Email':item[4],
                'Created':item[5],
                }
            result_json.append(user)
        #result=self.image_api.get_images()
        #if result.status_code == 200:
        #    result_json=result.json()
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
        user_name=request.json.pop('user_name')
        cn_name=request.json.pop('cn_name')
        department=request.json.pop('department')
        email=request.json.pop('email')
        created=utils.human_readable_time(time.time()) 
        self.db_api.add_user(user_name,cn_name,department,email,created)
        result_json = {}
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
