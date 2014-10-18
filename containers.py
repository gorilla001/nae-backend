import webob
import webob.dec
import requests
import json
import ast
import config
from images import ImageAPI
import urllib
from pprint import pprint
import utils
import os
from database import DBAPI
import time
import ast
from utils import MercurialControl

import eventlet
eventlet.monkey_patch()


class ContainerAPI():
    def __init__(self):
        self.url = "http://{}:{}".format(config.docker_host,config.docker_port) 
        self.db_api=DBAPI()
        self.headers={'Content-Type':'application/json'}
        self.name = None 
        self.repo_path = None 
        self.user_name = None 
        self._id = None 
    def create_container(self,kargs,name,repo_path,user_name,_container_id):
        self.name = name
        self.repo_path = repo_path
        self.user_name = user_name
        self._id = _container_id
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
            'Cmd' : [], 
            'Dns' : None,
            'Image' : None,
            'Volumes' : {},
            'VolumesFrom' : '',
            'ExposedPorts': {}
            
        }
        data.update(kargs)
        eventlet.spawn_n(self._create_container,data)
        result=webob.Response('{"status_code":200"}')
        return result
    def _create_container(self,data):
        _url = "{}/containers/create?name={}".format(self.url,self.name)
        resp = requests.post(_url,data=json.dumps(data),headers=self.headers)
        if resp.status_code == 201:
            container_info = resp.json()
            container_id = container_info["Id"]
            self.db_api.update_container(
            		id = self._id,
            		container_id = container_id, 
            		status = 'created'
            		)
            repo_name = os.path.basename(self.repo_path)	
            path=os.path.join(os.path.dirname(__file__),'files')
            source_path = os.path.join(path,self.user_name,repo_name)
            dest_path = "/mnt"
            kargs = {
              	'Binds':['{}:{}'.format(source_path,dest_path)],
            	'Dns':[config.DNS.strip("'")],
            }
            self.start_container(kargs,container_id)
    def delete_container(self,_container_id,container_id,v):
        self.db_api.update_container_status(
                id = _container_id,
                status = "stoping"
        )
        self.stop_container(container_id)
        self.db_api.update_container_status(
                id = _container_id,
                status = "deleting"
        )
        result=requests.delete("{}/containers/{}?v={}".format(self.url,container_id,v))    
        self.db_api.delete_container(_container_id)
        return result
    def get_containers(self):
        result=requests.get("{}/containers/json?all=0".format(self.url))    
        return result
    def get_container_by_id(self,container_id):
        result=requests.get("{}/containers/json?all=1".format(self.url))    
        response=webob.Response()
        for res in result.json():
            if container_id in res['Id']:
                pass
        return response 
    def start_container(self,kargs,container_id):
        data = {
            'Binds':[],
            'Links':[],
            'LxcConf':{},
	        'PortBindings':{},
            'PortBindings':{},
            'PublishAllPorts':True,
            'Privileged':False,
            'Dns':[],
            'VolumesFrom':[],
            'CapAdd':[],
            'CapDrop':[],
	    }
        data.update(kargs)
        eventlet.spawn_n(self._start_container,container_id,data)
        result=webob.Response('{"status_code":200"}')
        return result

    def _start_container(self,container_id,data):
        _url="{}/containers/{}/start".format(self.url,container_id)
        result=requests.post(_url,data=json.dumps(data),headers=self.headers)  
        print 'result.status_code' ,result.status_code
        if result.status_code == 204:
            self.db_api.update_container_status(
        			id = self._id,
        			status = "ok"
        	)
            result=self.inspect_container(container_id)
            network_settings = result.json()['NetworkSettings']
            ports=network_settings['Ports']
            private_host = network_settings['IPAddress']
            #network_config=list()
            for port in ports:
            		private_port = port.rsplit('/')[0]
            		for item in ports[port]:
                		host_ip=item['HostIp']
                		host_port=item['HostPort']
            		#network_config.append("{}:{}->{}".format(host_ip,host_port,private_port))
                        self.db_api.add_network(
                            container_id = container_id,
                            pub_host = host_ip,
                            pub_port = host_port,
                            pri_host = private_host,
                            pri_port = private_port,
                        )
            #self.db_api.update_container_network(
        	#	id = self._id,
        	#	network = str(network_config),
            #)
        if result.status_code == 500:
            self.db_api.update_container_status(
        			id = self._id,
        			status = "500"
        )
    def stop_container(self,container_id):
        result=requests.post("{}/containers/{}/stop?t=300".format(self.url,container_id))
        return result
    def kill_container(self,container_id):
        result=requests.post("{}/containers/{}/kill".format(self.url,container_id))
        return result
    def inspect_container(self,container_id):
        result=requests.get("{}/containers/{}/json".format(self.url,container_id))
        return result


class ContainerController(object):
    def __init__(self):
        self.compute_api=ContainerAPI()
        self.image_api=ImageAPI()
        self.db_api = DBAPI()
        self.mercurial = MercurialControl()
    @webob.dec.wsgify
    def __call__(self,request):
        method=request.environ['wsgiorg.routing_args'][1]['action']
        method=getattr(self,method)     
        response=webob.Response()
        result_json=method(request)
        response.headers.add("Content-Type","application/json")
        response.json=result_json
        return response
    def index(self,request):
        project_id = request.GET.get('project_id')
        user_id = request.GET.get('user_id')

        rs = self.db_api.get_containers(project_id,user_id)
        container_list = list()
        for item in rs.fetchall():
            container = {
                    'ID':item[0],
                    'Name':item[2],
		            #'AccessMethod':'  '.join(ast.literal_eval(item[7])),
		            'AccessMethod':'',
                    'Created':item[8],
                    'Status':item[10],
                    }
            container_id = item[1]
            network_info = self.db_api.get_network(container_id)
            network_list = list()
            for net in network_info.fetchall():
                pub_host = net[2]
                pub_port = net[3]
                pri_port = net[5]
                network_config ="{}:{}~{}".format(pub_host,pub_port,pri_port)
                network_list.append(network_config)
            data = {
                "AccessMethod":' '.join(network_list),
            }
            container.update(data)
            container_list.append(container)
        return container_list
    def show(self,request):
        container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        container_info = self.db_api.get_container(container_id).fetchone()
        project_info=self.db_api.get_project(container_info[4]).fetchone()
        container = {
                'name':container_info[2],
                'id':container_info[1],
                'env':container_info[3],
                'project':project_info[1],
                'hgs':container_info[5],
                'code':container_info[6],
                'access':' '.join(ast.literal_eval(container_info[7])),
                'created':container_info[8],
                'createdby':container_info[9],
                'status':container_info[10],
                }
        return container
    def inspect(self,request):
        container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        result=requests.get("http://0.0.0.0:2375/containers/{}/json".format(container_id))
        return result
    def delete(self,request):
        result_json={"status":"200"}
        _container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        _v = request.GET.get('v')
        container_info = self.db_api.get_container(_container_id).fetchone()
        container_id = container_info[1]
        eventlet.spawn_n(self.compute_api.delete_container,_container_id,container_id,_v)
        return result_json
    def create(self,request):
        container_image=request.json.pop('container_image')
        container_env = request.json.pop('container_environ')
        project_id = request.json.pop('container_project')
        container_hg=request.json.pop('container_hg')
        container_code = request.json.pop('container_code')
        root_path = request.json.pop('root_path')
        user_name = request.json.pop('user_name')
        user_key = request.json.pop('user_key')

        container_name = os.path.basename(container_hg) + '-' + container_code 
        max_id = self.db_api.get_max_container_id()
        max_id = max_id.fetchone()[0]
        if max_id is not None:
            max_id = max_id + 1;
        else:
            max_id = 0;
        container_name = container_name + '-' + str(max_id).zfill(4)
        #container_name = container_name + '-' + utils.random_str(4) 
        created_time = utils.human_readable_time(time.time())
        _container_id = self.db_api.add_container(
                container_name=container_name,
                container_env=container_env,
                project_id=project_id,
                container_hg=container_hg,
                container_code=container_code,
                created=created_time,
                created_by=user_name,
                status="building")

        self.prepare_start_container(user_name,user_key,container_hg,container_code,container_env)
        self.start_container(container_name,container_image,container_hg,container_code,root_path,container_env,user_key,user_name,_container_id)
    	#self.start_container(container_id,user_name,container_hg)
        
    def start_container(self,name,image,repo_path,branch,root_path,app_env,ssh_key,user_name,_container_id):
        image_info = self.db_api.get_image(image).fetchone()
        image_id = image_info[1]
        result=self.image_api.inspect_image(image_id)
        result_json=result.json()
        port=result_json['Config']['ExposedPorts']
        kwargs={
                'Image':image_id,
	    'Env':[
	          "REPO_PATH={}".format(repo_path),
	          "BRANCH={}".format(branch),
	          "ROOT_PATH={}".format(root_path),
	          "APP_ENV={}".format(app_env),
                      "SSH_KEY={}".format(ssh_key),
	    	],
            	'Cmd' : ["/opt/start.sh"], 
                'ExposedPorts':port,
	    
            }
        self.compute_api.create_container(kwargs,name,repo_path,user_name,_container_id)
    def prepare_start_container(self,user,key,hg,branch,env):
        user_home=utils.make_user_home(user,key)
        repo_name=os.path.basename(hg)
        if utils.repo_exist(user,repo_name):
            self.mercurial.pull(user,hg)
        else:
            self.mercurial.clone(user,hg)
        self.mercurial.update(user,hg,branch)

    #def start_container(self,container_id,user_name,repo_path):
#	repo_path = os.path.basename(repo_path)	
#	path=os.path.join(os.path.dirname(__file__),'files')
#	source_path = os.path.join(path,user_name,repo_name)
#	dest_path = "/mnt"
#	kargs = {
#            'Binds':['{}:{}'.format(source_path,dest_path)],
#            'Dns':[config.DNS.strip("'")],
#	}
#        self.compute_api.start_container(kargs,container_id)

    
    def get_container_info(self,name):
        result=self.compute_api.inspect_container(name)
        container_id = result.json()['Id'][:12]
        network_settings = result.json()['NetworkSettings']
        ports=network_settings['Ports'] 
        private_host = network_settings['IPAddress']
        network_config=list()
        for port in ports:
            private_port = port.rsplit('/')[0] 
            for item in ports[port]:
                host_ip=item['HostIp']
                host_port=item['HostPort']
            #network_config.append("{}:{}->{}:{}".format(host_ip,host_port,private_host,private_port))
            network_config.append("{}:{}->{}".format(host_ip,host_port,private_port))
        return (container_id,network_config,)

                
