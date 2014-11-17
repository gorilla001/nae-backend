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
        #project_id=request.environ['wsgiorg.routing_args'][1]['project_id']
        project_id = request.GET.get('project_id')
        rs = self.db_api.get_users(project_id=project_id)
        for item in rs.fetchall():
            user={
                'Id':item[0],
                'UserID':item[1],
                'Email':item[2],
                'RoleID':item[5],
                'Created':item[6],
                }
            result_json.append(user)
        return result_json

    def show(self,request):
        user_id=request.environ['wsgiorg.routing_args'][1]['id']
	proj_id=request.GET.get('project_id')
	_user_info=self.db_api.get_user(user_id,proj_id)	
	user_info=_user_info.fetchone()	
	if user_info is not None:
	    user = {
		"UserID":user_info[1],
		"Email":user_info[2],
		"RoleID":user_info[5],
	    }
            return user 
	return {}

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
        user_id=request.json.pop('user_name')
        email=request.json.pop('user_email')
        role_id=request.json.pop('role_id')
        project_id=request.json.pop('project_id')
        created=utils.human_readable_time(time.time()) 
        self.db_api.add_user(
                user_id = user_id,
                user_email = email,
                role_id = role_id,
                project_id = project_id,
                created = created,
        )
        result_json = {"status":200}
        return result_json
    def delete(self,request):
        user_id=request.environ['wsgiorg.routing_args'][1]['id']
        self.db_api.delete_user(user_id)
        result='{"status":200}'
        return result
