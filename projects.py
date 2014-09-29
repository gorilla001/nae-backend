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



class ProjectAPI():
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
        



class ProjectController(object):
    @webob.dec.wsgify
    def __call__(self,request):
        method=request.environ['wsgiorg.routing_args'][1]['action']
        method=getattr(self,method)     
        response=webob.Response()
        result_json=method(request)
        response.json=result_json
        return response
    def __init__(self):
        self.project_api=ProjectAPI()
        self.db_api=DBAPI()
    def index(self,request):
        result_json=[]
        rs = self.db_api.get_projects()
        for item in rs.fetchall():
            project={
                'ProjectId':item[0],
                'ProjectName':item[1],
                'ProjectDesc':item[2],
                'ProjectHgs':item[3],
                'ProjectImgs':item[4],
                'ProjectAdmin':item[5],
                'ProjectMembers':'',
                'CreatedTime':item[7],
                }
            rs = self.db_api.get_users(project_id=item[0])
            user_list =list()
            for user in rs.fetchall():
                user_list.append(user[1])
            user_list=' '.join(user_list)
            data =  { 'ProjectMembers':user_list}
            project.update(data)
            result_json.append(project)
        #result=self.image_api.get_images()
        #if result.status_code == 200:
        #    result_json=result.json()
        return result_json
    def show(self,request):
        project_id=request.environ['wsgiorg.routing_args'][1]['id']
        result = self.db_api.get_projects(project_id=project_id)
        project_info = result.fetchone()
        project_name= project_info[1]
        project_desc = project_info[2]
        project_hgs = project_info[3]
        project_admin = project_info[5]
        _members = self.db_api.get_users(project_id=project_id)
        project_members=list()
        for memb in _members.fetchall():
               project_members.append(memb[1]) 
        project_members=' '.join(project_members)
        project_created = project_info[7]
        result = self.db_api.get_images(project_id=project_id)
        project_imgs=[]
        for item in result.fetchall():
            img_name = item[2]
            project_imgs.append(img_name)
        project_imgs=' '.join(project_imgs)
        print project_imgs
        result_json={}
        result_json = {
                    "name":project_name,
                    "desc":project_desc,
                    "admin":project_admin,
                    "members":project_members,
                    "hgs":project_hgs,
                    "imgs":project_imgs,
                    "created":project_created,
                    }
        print result_json
        #if result.status_code == 200:
        #    for res in result.json():
        #        if image_id in res['Id']:
        #            result_json = res   
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
        project_name=request.json.pop('project_name')
        project_hgs=request.json.pop('project_hgs')
        project_admin=request.json.pop('project_admin')
        project_members=request.json.pop('project_members')
        project_desc=request.json.pop('project_desc')
        created_time = utils.human_readable_time(time.time())

        print project_name,project_hgs,project_members,project_admin,project_desc
        #add_project(self,project_name,project_hgs,project_admin,project_members,project_desc,created_time)
        project_id=self.db_api.add_project(
                str(project_name),
                ' '.join(project_hgs),
                str(project_admin),
                #' '.join(project_members),
                '',
                str(project_desc),
                str(created_time),
                )
        for member in project_members:
            self.db_api.add_user(
                    user_id = member,
                    user_name = '',
                    project_id = project_id,
                    created = created_time,
                    )
        #self.db_api.add_user(
        #        )
        result_json={}
        return result_json
    def delete(self,request):
        project_id=request.environ['wsgiorg.routing_args'][1]['id']
        self.db_api.delete_project(project_id)
        #result=self.image_api.delete_image(image_id)
        #if result.status_code == 200:
        #    result_json = result.json() 
        #if result.status_code == 404:
        #    errors={"errors":"404 Not Found:no such image {}".format(image_id)}
        #    result_json=errors
        #if result.status_code == 409:
        #    errors={"errors":"409 conflict"}
        #    result_json=errors
        #if result.status_code == 500:
        #    errors={"errors":"500 internal server error"}
        #    result_json=errors
        result_json={}
        return result_json

def create_resource():
    return ProjectController()
