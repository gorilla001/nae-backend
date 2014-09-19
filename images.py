import webob
import webob.dec
import requests
import json
import config
from database import DBAPI
from utils import MercurialControl
import os
import utils



class ImageAPI():
    def __init__(self):
        self.url="http://{}:{}".format(config.docker_host,config.docker_port)
        self.mercurial = MercurialControl()
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
    def create_image_from_file(self,image_name,repo_path):

        repo_name=os.path.basename(repo_path)
        if utils.repo_exist(repo_name):
            self.mercurial.pull(repo_path)
        else:
            self.mercurial.clone(repo_path)
        file_path=utils.get_file_path(repo_name)
        tar_path=utils.make_zip_tar(file_path)
        print tar_path
        data=open(tar_path,'rb')
        headers={'Content-Type':'application/tar'}
        result=requests.post("{}/build?t={}".format(self.url,image_name),headers=headers,data=data)
        #url='http://localhost:2375/build?t=test33&nocache'
        #files=open('/tmp/httpd/httpd.tar.gz','rb')

        #r=requests.post(url,data=files,headers=headers)
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
        result_json=[]
        rs = self.db_api.select_images()
        for item in rs.fetchall():
            image={
                'ImageId':item[0],
                'ImageName':item[1],
                'ImageSize':item[2],
                'ImageDesc':item[3],
                'CreatedTime':item[4],
                'CreatedBy':item[5],
                }
            result_json.append(image)
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
        image_name=request.json.pop('image_name')
        image_desc=request.json.pop('image_desc')
        repo_path=request.json.pop('repo_path')
        user_name=request.json.pop('user_name')

        print image_name,image_desc,repo_path,user_name
        result_json={}
        result=self.image_api.create_image_from_file(image_name,repo_path)
        if result.status_code == 200:
            print 'image create ok'
            result_json={"ok":"200 create image successful"}
            result=self.image_api.inspect_image(image_name)
            image_id=result.json()['id'][:12]
            result = self.image_api.get_image_by_id(image_id)
            for res in result.json():
                if image_id in res['Id']:
                    image_size=res['VirtualSize']
                    created_time = res['Created'] 
            image_size = utils.human_readable_size(image_size)
            created_time = utils.human_readable_time(created_time)
            created_by = user_name
            print image_id,image_name,image_size,image_desc,created_time,created_by
            self.db_api.insert_image(image_id,image_name,image_size,image_desc,created_time,created_by)
        if result.status_code == 500:
            errors={"errors":"500 internal server error"} 
            result_json=errors
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
