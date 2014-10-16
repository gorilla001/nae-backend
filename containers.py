import webob
import webob.dec
import requests
import json
import ast
#from database import DB
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

class ContainerAPI():
    def __init__(self):
        self.url = "http://{}:{}".format(config.docker_host,config.docker_port) 
    def create_container(self,kargs,repo_path,branch,root_path,app_env,ssh_key,name):
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
	    'Env':[
		      "REPO_PATH={}".format(repo_path),
		      "BRANCH={}".format(branch),
		      "ROOT_PATH={}".format(root_path),
		      "APP_ENV={}".format(app_env),
                      "SSH_KEY={}".format(ssh_key),
	    ],
            'Cmd' : ["/opt/start.sh"], 
            'Dns' : None,
            'Image' : None,
            'Volumes' : {},
            'VolumesFrom' : '',
            'ExposedPorts': {},
        }
        data.update(kargs)
        pprint(data)
        headers={'Content-Type':'application/json'}
        resp = requests.post("{}/containers/create?name={}".format(self.url,name),data=json.dumps(data),headers=headers)
        return resp
    def delete_container(self,container_id):
        result=requests.delete("{}/containers/{}".format(self.url,container_id))    
        return result
    def get_containers(self):
        result=requests.get("{}/containers/json?all=0".format(self.url))    
        return result
    def get_container_by_id(self,container_id):
        result=requests.get("{}/containers/json?all=1".format(self.url))    
        response=webob.Response()
        for res in result.json():
            if container_id in res['Id']:
            #response.json = res    
                pass
        return response 
    def start_container(self,container_id,exposed_port,user_name,repo_name):
        random_port=utils.get_random_port()
	path=os.path.join(os.path.dirname(__file__),'files')
	source_path = os.path.join(path,user_name,repo_name)
	dest_path = "/mnt"
        data = {
            'Binds':['{}:{}'.format(source_path,dest_path)],
            'Links':[],
            'LxcConf':{},
            'PortBindings':{exposed_port:[{'HostPort':'{}'.format(random_port)}]},
            'PublishAllPorts':True,
            'Privileged':False,
            'Dns':[config.DNS.strip("'")],
            'VolumesFrom':[],
            'CapAdd':[],
            'CapDrop':[],
	}
        headers={"Content-Type":"application/json"}
        result=requests.post("{}/containers/{}/start".format(self.url,container_id),data=json.dumps(data),headers=headers)  
        return result
    def stop_container(self,container_id):
        result=requests.post("{}/containers/{}/stop?t=3".format(self.url,container_id))
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
        #print request.environ['wsgiorg.routing_args']
        #print request.method
        method=request.environ['wsgiorg.routing_args'][1]['action']
        #print '----------------'
        #print method
        #print '----------------'
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
                    'AccessMethod':' '.join(ast.literal_eval(item[7])),
                    'Created':item[8],
                    'Status':item[10],
                    }
            rs = self.db_api.get_sftp(item[1])
            sftp_info = rs.fetchone()
            print sftp_info 
            sftp_addr = sftp_info[2]
            sftp_user = sftp_info[3]
            sftp_port = sftp_info[4]
            data = { 'Sftp' : '{}@{}:{}'.format(sftp_user,sftp_addr,sftp_port) }
            container.update(data)
            container_list.append(container)
        #containers=self.compute_api.get_containers()
        #container_list=list()
        #for item in containers.json():
        #    container = {
        #            'Id':item['Id'][:12],
        #            'Name':item['Names'][0][1:],
        #            'Status':item['Status'],
        #    }
        #    for i in item['Ports']:
        #        try :
        #            IP = i.get('IP')
        #            PUB_PORT = i.get('PublicPort')
        #            PRI_PORT = i.get('PrivatePort')
        #            
        #            data = { 'Ports':'{}:{}->{}'.format(IP,PUB_PORT,PRI_PORT)}
        #            container.update(data)
        #            print i["State"]
        #        except KeyError: 
        #            continue
        #    container_list.append(container)
                    
        return container_list
    def show(self,request):
        container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        #container=self.compute_api.get_container_by_id(container_id)
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
        print container
        return container
    def inspect(self,request):
        container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        result=requests.get("http://0.0.0.0:2375/containers/{}/json".format(container_id))
        #if result.status_code == 200:
        #   response.json=json.dumps(dict(result.json()))
        #if result.status_code == 404:
        #   errors={"errors":"404 Not Found:no such container {}".format(container_id)}
        #   response.json=errors
        #   
        return result
    def delete(self,request):
        result_json={}
        _container_id=request.environ['wsgiorg.routing_args'][1]['container_id']
        container_info = self.db_api.get_container(_container_id).fetchone()
        container_id = container_info[1]
        result=self.compute_api.kill_container(container_id)
        if result.status_code == 204:
            result_json = {"succeed":"{} stopped".format(container_id)}
        if result.status_code == 404:
            result_json = {"error":"404 no such container"}
            return result_json
        if result.status_code == 500:
            result_json = {"error":"500 server error"}
            return result_json
            result=self.compute_api.delete_container(container_id)
        if result.status_code == 204:
            result_json = {"succeed":"{} deleted".format(container_id)}
            self.db_api.delete_container(_container_id)
        if result.status_code == 400:
            result_json = {"error":"400 bad parameter"} 
        if result.status_code == 404:
            result_json = {"error":"404 no such container"}
        if result.status_code == 500:
            result_json = {"error":"500 internal server error"}
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

        container_name,container_id,container_port = self.create_container(container_image,container_hg,container_code,root_path,container_env,user_key)
	self.prepare_start_container(user_name,user_key,container_hg,container_code,container_env)
    	self.start_container(container_id,container_port,user_name,os.path.basename(container_hg))
        self.save_to_db(container_id,container_name,container_env,project_id,container_hg,container_code,user_name)
        
    def create_container(self,image,repo_path,branch,root_path,app_env,ssh_key):
        result = self.image_api.inspect_image(image)
        result_json={}
        if result.status_code == 200:
            result_json=result.json()   
            port=result_json['Config']['ExposedPorts']
            name=utils.random_str()
            kwargs={
                'Image':image,
                'ExposedPorts':port,
            }
            resp = self.compute_api.create_container(kwargs,repo_path,branch,root_path,app_env,ssh_key,name)
            if resp.status_code == 201:
                _container_id = resp.json()['Id']
                return (name,_container_id,port.keys()[0])
        if result.status_code == 404:
            errors={"errors":"404 Not Found:no such image {}".format(image)}
            result_json=errors
            return result_json

    def prepare_start_container(self,user,key,hg,branch,env):
        user_home=utils.make_user_home(user,key)
        repo_name=os.path.basename(hg)
        if utils.repo_exist(user,repo_name):
            self.mercurial.pull(user,hg)
            self.mercurial.update(user,hg)
        else:
            self.mercurial.clone(user,hg)
        #self.mercurial.update(user,hg,branch)
        #utils.prepare_config_file(user_home,repo_name,env)
        #utils.change_dir_owner(user_home,user)

    def start_container(self,container_id,exposed_port,user_name,repo_name):
        self.compute_api.start_container(container_id,exposed_port,user_name,repo_name)

    def save_to_db(self,id,name,env,project_id,hg,branch,user):
        network_config = self.get_container_info(name)[1]
        created_time = utils.human_readable_time(time.time())
        self.db_api.add_container(
                container_id=id,
                container_name=name,
                container_env=env,
                project_id=project_id,
                container_hg=hg,
                container_code=branch,
                access_method=str(network_config),
                created=created_time,
                created_by=user,
                status='ok')
        self.db_api.add_sftp(
                container_id = id,
                sftp_addr = config.HOST.strip("'"),
                sftp_user = user,
        )


    def get_container_info(self,name):
        result=self.compute_api.inspect_container(name)
        container_id = result.json()['Id'][:12]
        network_settings = result.json()['NetworkSettings']
        ports=network_settings['Ports'] 
        private_host = network_settings['IPAddress']
        network_config=list()
        for port in ports:
            private_port = port 
            for item in ports[port]:
                host_ip=item['HostIp']
                host_port=item['HostPort']
            network_config.append("{}:{}->{}:{}".format(host_ip,host_port,private_host,private_port))
        return (container_id,network_config,)

                
