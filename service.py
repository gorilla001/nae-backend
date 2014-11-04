import threadgroup

class Service(object):
    def __init__(self,server):
	self.service = server
	self.tg = threadgroup.ThreadGroup()
    def start(self):
	self.tg.start_thread(self.run_service,self.service)
    def run_service(service):
	service.start()
	service.wait()	
