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
import log

import eventlet
eventlet.monkey_patch()

logger=log.getlogger()



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
    def create_image_from_file(self,id,image_name,repo_path,repo_branch,user_name):

        repo_name=os.path.basename(repo_path)
        if utils.repo_exist(user_name,repo_name):
            self.mercurial.pull(user_name,repo_path)
        else:
            self.mercurial.clone(user_name,repo_path)
        self.mercurial.update(user_name,repo_path,repo_branch)
        file_path=utils.get_file_path(user_name,repo_name)
        tar_path=utils.make_zip_tar(file_path)
        def create_image(url,image_name,tar_path,id):
            data=open(tar_path,'rb')
            headers={'Content-Type':'application/tar'}
            rs=requests.post("{}/build?t={}".format(url,image_name),headers=headers,data=data)
	    with open("/tmp/aaabbb",'w') as f:
	    	f.write('{}'.format(rs.status_code))
	    if rs.status_code == 200:
            	result=self.inspect_image(image_name)
		if result.status_code == 200:
            		image_id=result.json()['Id'][:12]
            		result = self.get_image_by_id(image_id)
            		for res in result.json():
                    	    if image_id in res['Id']:
                   	        image_size=res['VirtualSize']
            		image_size = utils.human_readable_size(image_size)
            		self.db_api.update_image(
				  id=id,
                                  image_id=image_id,
                                  size=image_size,
                                  status = "ok")
		if result.status_code == 404:
			self.db_api.update_image(
				  id=id,
                                  image_id='',
                                  size='',
                                  status = "404")
		if result.status_code == 500:
			self.db_api.update_image(
				  id=id,
                                  image_id='',
                                  size='',
                                  status = "500")
	    if rs.status_code == 500:
		self.db_api.update_image(
				  id=id,
                                  image_id='',
                                  size='',
                                  status = "500")
        eventlet.spawn_n(create_image,self.url,image_name,tar_path,id)
        result=webob.Response('{"status_code":200"}')
        return result
    def delete_image(self,id,image_id,f_id):
        def _delete_image(url,image_id,f_id,id):
		result=requests.delete("{}/images/{}?force={}".format(url,image_id,f_id))
		status_code = result.status_code 
		if status_code == 200 or status_code == 404:
			self.db_api.delete_image(id)
		if status_code == 409: 
			self.db_api.update_image_status(
				  id=id,
                                  status = "409")
		if status_code == 500: 
			self.db_api.update_image_status(
				  id=id,
                                  status = "500")
        eventlet.spawn_n(_delete_image,self.url,image_id,f_id,id)
        result=webob.Response('{"status_code":200"}')
        return result
    def edit(self,kargs,name,port):
        eventlet.spawn_n(self._edit,kargs,name,port)
        result=webob.Response('{"status_code":200"}')
        return result
    def _edit(self,kwargs,name,port):
	data = {
            'Hostname' : '',
            'User'     : '',
            'Memory'   : '',
            'MemorySwap' : '',
            'AttachStdin' : False,
            'AttachStdout' : False,
            'AttachStderr': False,
            'PortSpecs' : [],
            'Tty'   : True,
            'OpenStdin' : True,
            'StdinOnce' : False,
	    'Env':[],
	    'Cmd':["/opt/webssh/term.js/example/index.js"],
            'Dns' : None,
            'Image' : None,
            'Volumes' : {},
            'VolumesFrom' : '',
            'ExposedPorts': {
			"17698/tcp": {},
			}
            
        }
	data.update(kwargs)
        _url = "{}/containers/create?name={}".format(self.url,name)
        headers={'Content-Type':'application/json'}
        resp = requests.post(_url,data=json.dumps(data),headers=headers)
        if resp.status_code == 201:
		data = {
            		'Binds':[],
            		'Links':[],
            		'LxcConf':{},
            		'PublishAllPorts':False,
			'PortBindings':{ 
				"17698/tcp": [
					{ 
					    "HostIp":config.docker_host,
					    "HostPort":"{}".format(port), 
					}
				] 
			},
			"Cmd":["/opt/webssh/term.js/example/index.js"],
            		'Privileged':False,
            		'Dns':[],
            		'VolumesFrom':[],
            		'CapAdd':[],
            		'CapDrop':[],
	    	}
		ctn_id = resp.json()['Id']
        	_url="{}/containers/{}/start".format(self.url,ctn_id)
        	headers={'Content-Type':'application/json'}
        	result=requests.post(_url,data=json.dumps(data),headers=headers)  
        	if result.status_code != 204:
		    logger.debug("start for-image-edit container failed")	
	else:
	    logger.debug("create for-image-edit container failed") 

    def commit(self,repo,tag,ctn):
        eventlet.spawn_n(self._commit,repo,tag,ctn)
        result=webob.Response('{"status_code":200"}')
        return result
    def _commit(self,repo,tag,ctn):
        rs=self.inspect_container(ctn)
        if rs.status_code == 200:
            data=rs.json()['Config']
       	    _url="{}/commit?author=&comment=&container={}&repo={}&tag={}".format(self.url,repo,tag,ctn)
       	    result=requests.post(_url,data=json.dumps(data),headers=self.headers)  
            if result.status_code == 201:
		img_info=self.db_api.get_image_by_repo_tag(repo,tag)
		self.db_api.add_image(
                                  name=repo,
				  tag=tag,
                                  desc=img_info[6],
                                  project_id=img_info[7],
                                  repo = img_info[8],
				  branch = img_info[9], 
                                  created= created_time,
                                  owner=img_info[11],
                                  status = 'ok'
				)


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
            project_info = self.db_api.show_project(project_id=item[6]) 
            project_name = project_info.fetchone()[1]
            image={
                'ID':item[0],
                'ImageId':item[1],
                'ImageName':item[2],
		'ImageTag':item[3],
                'ImageSize':item[4],
                'ImageDesc':item[5],
                'ImageProject':project_name,
                'CreatedTime':item[9],
                'CreatedBy':item[10],
                'Status' : item[11],
                }
            result_json.append(image)
        return result_json
    def show(self,request):
        image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
        result = self.db_api.get_image(image_id)
        image_info=result.fetchone()
        image={
                'ImageID':image_info[1],
                'ImageName':image_info[2],
                'ImageSize':image_info[3],
                'ImageDesc':image_info[4],
                'RepoPath':image_info[6],
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
	id=self.db_api.add_image(
                                  name=image_name,
				  tag="latest",
                                  desc=image_desc,
                                  project_id=project_id,
                                  repo = repo_path,
				  branch = repo_branch, 
                                  created= created_time,
                                  owner=user_name,
                                  status = 'building'
	)
        self.image_api.create_image_from_file(id,image_name,str(repo_path),str(repo_branch),user_name)
        result_json={}
        return result_json
    def delete(self,request):
        _image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
        f_id=request.GET['force']
        image_info = self.db_api.get_image_by_id(_image_id).fetchone()
        image_id=image_info[1]
	self.db_api.update_image_status(
				  id=_image_id,
                                  status = "deleting")
        self.image_api.delete_image(_image_id,image_id,f_id)
    def edit(self,request):
        _img_id=request.GET.pop('id')
        _img_info = self.db_api.get_image(_img_id).fetchone()
        img_id = _img_info[1]
	name = utils.random_str()
	port = utils.get_random_port()
	kwargs={
		"Image":img_id,
	    	}
	eventlet.spawn_n(self.image_api.edit,kwargs,name,port)
	
	return {
		"url":"http://{}:{}".format(config.docker_host,port),
		"name":name,
		}
    def commit(self,request):
	repo = request.GET.pop('repo')
	tag = request.GET.pop('tag')
	ctn = request.GET.pop('ctn')
	self.image_api.commit(repo,tag,ctn)


def create_resource():
    return ImageController()
