#!/usr/bin/env python

from eventlet import wsgi
import eventlet
from paste.deploy import loadapp
import os
import requests
import log
import config

config_file='paste.ini'
appname='api'

docker_url=('http://{}:{}/info'.format(config.docker_host,config.docker_port))
print docker_url
r=requests.get(docker_url)
if r.status_code != 200:
    log.LOG('cannot connect to docker!!!')
else:
    log.LOG(r.json())

app=loadapp('config:{}'.format(os.path.abspath(config_file)),name=appname)
wsgi.server(eventlet.listen(('',8282)),app)
