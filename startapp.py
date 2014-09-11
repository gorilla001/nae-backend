from eventlet import wsgi
import eventlet
from paste.deploy import loadapp
import os

config='paste.ini'
appname='api'

app=loadapp('config:{}'.format(os.path.abspath(config)),name=appname)
wsgi.server(eventlet.listen(('',8383)),app)
