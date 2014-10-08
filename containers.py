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
    def create_container(self,kargs,name):
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
            'Env' : None,
            'Cmd' : [], 
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
        return result 
    def start_container(self,container_id,exposed_port,root_path,repo_name,user_name):
        random_port=utils.get_random_port()
        path=os.path.join(os.path.dirname(__file__),'files')
        _path = os.path.join(path,user_name)
        source_path = os.path.join(_path,repo_name)
        print 'source_path',source_path
        dest_path = root_path
        print 'dest_path',dest_path
        data = {
            'Binds':['{}:{}'.format(source_path,dest_path)],
            'Links':[],
            'LxcConf':{},
            'PortBindings':{exposed_port:[{'HostPort':'{}'.format(random_port)}]},
            'PublishAllPorts':True,
            'Privileged':False,
            'Dns':[config.DNS],
            'VolumesFrom':[],
            'CapAdd':[],
            'CapDrop':[],
        }
        pprint(data)
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
        result=requests.get("http://0.0.0.0:2375/containers/{}/json".format(container_id))
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
        rs = self.db_api.get_containers()
        container_list = list()
        for item in rs.fetchall():
            container = {
                    'ID':item[0],
                    'Name':item[2],
                    'AccessMethod':' '.join(ast.literal_eval(item[7])),
                    'Created':item[8],
                    'Status':item[10],
                    }
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
        container_hgs=request.json.pop('container_image')
        container_env = request.json.pop('container_environ')
        project_id = request.json.pop('container_project')
        container_code = request.json.pop('container_code')
        root_path = request.json.pop('root_path')
        user_name = request.json.pop('user_name')
        user_key = request.json.pop('user_key')
        #cmd=body.pop('Cmd')
        #image=self.db_api.get_image_by_hgs(container_hgs).fetchone()[2]
        repo_path = container_hgs
        repo_name=os.path.basename(container_hgs)
        user_home=utils.make_user_home(user_name,user_key)
        if utils.repo_exist(user_name,repo_name):
            self.mercurial.pull(user_name,repo_path)
            self.mercurial.update(user_name,repo_path)
        else:
            self.mercurial.clone(user_name,repo_path)
        #self.mercurial.update(repo_path,container_code)
        utils.change_dir_owner(user_home,user_name)
        image=os.path.basename(container_hgs)
        result = self.image_api.inspect_image(image)
        result_json={}
        if result.status_code == 200:
            result_json=result.json()   
        if result.status_code == 404:
            errors={"errors":"404 Not Found:no such image {}".format(image)}
            result_json=errors
            return result_json
        port=result_json['config']['ExposedPorts']
        #name=request.params['name']
        name=utils.random_str()
        kwargs={
            'Image':image,
            #'Cmd':[cmd],
            'ExposedPorts':port,
        }
        resp=self.compute_api.create_container(kwargs,name)
        result_json={}
        if resp.status_code == 201:
            result_json = resp.json() 
            #container_id=result_json['Id']
            resp = self.compute_api.start_container(result_json['Id'],port.keys()[0],root_path,repo_name,user_name)
        
            #print result.json()['HostConfig']
            if resp.status_code == 204:
                result_json={"succeed":"start ok"}
                container_id = self.get_container_info(name)[0]
                network_config = self.get_container_info(name)[1]
                created_time = utils.human_readable_time(time.time())
                self.db_api.add_container(
                        container_id=container_id,
                        container_name=name,
                        container_env=container_env,
                        project_id=project_id,
                        container_hgs=container_hgs,
                        container_code=container_code,
                        access_method=str(network_config),
                        created=created_time,
                        created_by=user_name,
                        status='ok')
                #utils.create_user_access(user_name)

            if resp.status_code == 304:
                result_json={"error":"304 container already started"}
            if resp.status_code == 404:
                result_json={"error":"404 no such container"}
            if resp.status_code == 500:
                result_json={"error":"500 server error"}    
        if resp.status_code == 404:
            result_json = {"error":"404 no such image:{}".format(Image)}
        if resp.status_code == 406:
            result_json = {"error":"impossible to attach(container not running)"}   
        if resp.status_code == 409:
            result_json = {"error":"409 Conflict, The name memcached6 is already assigned"}
        if resp.status_code == 500:
            result_json = {"error":"500 server error"}
        return result_json
            #if 'name' not in container_dict:
            #   msg = _("Container name is not defined")
            #   raise exc.HTTPBadRequest(explanation=msg)
        
            #image_id=self._image_from_req_data(body)
            #
            #command_context=self._command_from_req_data(body)
        
            #exposed_port=self._get_exposed_port(image_id)
        
            #self.compute_api.create_container(name,image_id,exposed_port,command_context)
            #params=list(request.POST)[0]
            #params_dict=ast.literal_eval(params)
            #cmd=params_dict.get('cmd')
            #image=params_dict.get('image') 
            #args={'Cmd':cmd,'Image':image} 
            #url="http://0.0.0.0:2375/container/create"
            #headers={'Content-Type':'application/json'}
            #result=requests.post(url,data=json.dumps(args),headers=headers)
            #print result.status_code
            #if result.status_code == 404:
            #   error={"error":"404 Not Found:no such image {}".format(image)}
            #   response.json=error
            #if result.status_code == 201:
            #   response.json=json.dumps(dict(result.json()))
            #if result.status_code == 500:
            #   error={"error":"500 internal server error"}
            #   response.json=error
    def get_container_info(self,name):
        result=self.compute_api.inspect_container(name)
        container_id = result.json()['ID'][:12]
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

                
