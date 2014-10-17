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
from pprint import pprint
import webob

import eventlet
eventlet.monkey_patch()



class ImageAPI():
    def __init__(self):
        self.url="http://{}:{}".format(config.docker_host,config.docker_port)
        self.mercurial = MercurialControl()
        self.db_api=DBAPI()
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
    def create_image_from_file(self,image_name,repo_path,repo_branch,project_id,user_name):

        repo_name=os.path.basename(repo_path)
        if utils.repo_exist(user_name,repo_name):
            self.mercurial.pull(user_name,repo_path)
        else:
            self.mercurial.clone(user_name,repo_path)
        self.mercurial.update(user_name,repo_path,repo_branch)
        file_path=utils.get_file_path(user_name,repo_name)
        tar_path=utils.make_zip_tar(file_path)
        print tar_path
        def create_image(url,image_name,tar_path,repo_path,project_id):
            data=open(tar_path,'rb')
            headers={'Content-Type':'application/tar'}
            requests.post("{}/build?t={}".format(url,image_name),headers=headers,data=data)
            result=self.inspect_image(image_name)
            pprint(result)
            image_id=result.json()['Id'][:12]
            result = self.get_image_by_id(image_id)
            for res in result.json():
                if image_id in res['Id']:
                    image_size=res['VirtualSize']
                    created_time = res['Created'] 
            image_size = utils.human_readable_size(image_size)
            self.db_api.update_image(
				  image_name=image_name,
                                  image_id=image_id,
                                  size=image_size,
                                  status = "ok")
        eventlet.spawn_n(create_image,self.url,image_name,tar_path,repo_path,project_id)
        result=webob.Response('{"status_code":200"}')
        return result
    def delete_image(self,image_id,f_id):
        result=requests.delete("{}/images/{}?force={}".format(self.url,image_id,f_id))
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
        result_json=[]
        project_id=request.GET.pop('project_id')
        rs = self.db_api.get_images(project_id=project_id)
        for item in rs.fetchall():
            project_info = self.db_api.show_project(project_id=item[5]) 
            #print '-----------------------'
            #print 'project_id',item[5]
            #print image_project.fetchone()
            #print '-----------------------'
            project_name = project_info.fetchone()[1]
            print project_name
            image={
                'ID':item[0],
                'ImageId':item[1],
                'ImageName':item[2],
                'ImageSize':item[3],
                'ImageDesc':item[4],
                'ImageProject':project_name,
                'CreatedTime':item[7],
                'CreatedBy':item[8],
                'Status' : item[9],
                }
            pprint(image)
            result_json.append(image)
        #result=self.image_api.get_images()
        #if result.status_code == 200:
        #    result_json=result.json()
        return result_json
    def show(self,request):
        image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
        #result = self.image_api.get_image_by_id(image_id)
        result = self.db_api.get_image_by_id(image_id)
        image_info=result.fetchone()
        project_info= self.db_api.get_project_by_id(image_info[5]).fetchone()
        image_hg = self.db_api.get_hg(image_info[1]).fetchone()[1]
        image={
                'ImageID':image_info[1],
                'ImageName':image_info[2],
                'ImageSize':image_info[3],
                'ImageDesc':image_info[4],
                'ProjectID':project_info[1],
                'ImageHgs':image_hg,
                'Created':image_info[7],
                'CreatedBy':image_info[8],
                'Status':image_info[9],
        }
        return image 
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
        project_id=request.json.pop('project_id')
        repo_path=request.json.pop('repo_path')
	repo_branch=request.json.pop('repo_branch')
        user_name=request.json.pop('user_name')

        created_time = utils.human_readable_time(time.time())
	self.db_api.add_image(
				  image_id='',
                                  name=image_name,
                                  size='',
                                  desc=image_desc,
                                  project_id=project_id,
                                  repo = repo_path,
				  branch = repo_branch, 
                                  created= created_time,
                                  created_by=user_name,
                                  status = 'building'
	)
        self.image_api.create_image_from_file(image_name,str(repo_path),str(repo_branch),image_proj,user_name)
        result_json={}
        return result_json
    def delete(self,request):
        _image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
        f_id=request.GET['force']
        image_info = self.db_api.get_image_by_id(_image_id).fetchone()
        image_id=image_info[1]
        result=self.image_api.delete_image(image_id,f_id)
        if result.status_code == 200:
            self.db_api.delete_image(_image_id)
            result_json = result.json() 
        if result.status_code == 404:
            errors={"errors":"404 Not Found:no such image {}".format(image_id)}
            self.db_api.delete_image(_image_id)
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
