import logging 

def getlogger():
    logger=logging.getLogger()
    hdlr=logging.FileHandler('/var/log/jaecpn/jaecpn.log')
    formatter=logging.Formatter('%(asctime)s %(levelname)s %(message)s','%Y-%m-%d %H:%M:%S')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    return logger

class WSGILogger(object):
    def __init__(self,logger,level=logging.INFO):
        self.logger = logger
        self.level = level 

    def write(self, msg):
	print msg.rstrip()
        self.logger.info(msg.rstrip())
        self.logger.log(self.level, msg.rstrip())
