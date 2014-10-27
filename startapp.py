#!/usr/bin/env python

from eventlet import wsgi
import eventlet
from paste.deploy import loadapp
import os
import requests
import log
import config
from daemon import Daemon

config_file='paste.ini'
appname='api'

Daemon().initDaemon()

logger=log.getlogger()

docker_url=('http://{}:{}/info'.format(config.docker_host,config.docker_port))
logger.debug(docker_url)
r=requests.get(docker_url)
if r.status_code != 200:
    logger.debug('cannot connect to docker!!!')
else:
    logger.debug(r.json())

app=loadapp('config:{}'.format(os.path.abspath(config_file)),name=appname)
application=wsgi.server(eventlet.listen(('',8282)),app,log=log.WSGILogger(logger))
