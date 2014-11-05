import logging 

def getlogger():
    logger=logging.getLogger()
    level=logging.NOTSET
    hdlr=logging.FileHandler('/var/log/jaecpn/jaecpn.log')
    formatter=logging.Formatter('%(asctime)s %(levelname)s %(message)s','%Y-%m-%d %H:%M:%S')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(level)
    return logger

class WSGILogger(object):
    def __init__(self,logger):
        self.logger = logger
    def write(self, msg):
        self.logger.log(logging.NOTSET, msg.rstrip())
        #self.logger.debug(msg.rstrip())
