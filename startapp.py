from eventlet import wsgi
import eventlet
from paste.deploy import loadapp
import os
import requests
import log

config='paste.ini'
appname='api'

r=requests.get('http://localhost:2375/info')
if r.status_code != 200:
    log.LOG('cannot connect to docker!!!')
else:
    log.LOG(r.json())

app=loadapp('config:{}'.format(os.path.abspath(config)),name=appname)
wsgi.server(eventlet.listen(('',8383)),app)
