from eventlet import patcher
from eventlet.green import ftplib, os, socket, time
from eventlet.green.http import client as http_client
from eventlet.green.urllib import error, parse, response

# TODO should we also have green email version?
# import email


to_patch = [
    ('http.client', http_client),
    ('os', os),
    ('socket', socket),
    ('time', time),
    ('urllib.error', error),
    ('urllib.parse', parse),
    ('urllib.response', response),
]

try:
    from eventlet.green import ssl
except ImportError:
    pass
else:
    to_patch.append(('ssl', ssl))

patcher.inject('urllib.request', globals(), *to_patch)
del to_patch

to_patch_in_functions = [('ftplib', ftplib)]
del ftplib

FTPHandler.ftp_open = patcher.patch_function(FTPHandler.ftp_open, *to_patch_in_functions)
URLopener.open_ftp = patcher.patch_function(URLopener.open_ftp, *to_patch_in_functions)

ftperrors = patcher.patch_function(ftperrors, *to_patch_in_functions)

ftpwrapper.init = patcher.patch_function(ftpwrapper.init, *to_patch_in_functions)
ftpwrapper.retrfile = patcher.patch_function(ftpwrapper.retrfile, *to_patch_in_functions)

del error
del parse
del response
del to_patch_in_functions
