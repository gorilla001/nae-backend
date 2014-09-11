from eventlet import pools
import kombu


class Pool(pools.Pool):
	MAX_SIZE=10
	def __init__(self,conf,connection_cls,**kwargs):
		self.connection = connection_cls
		self.conf = conf

		super(Pool,self).__init__(max_size=self.MAX_SIZE)

	def create(self):
		return self.connection(self.conf)		


def Connection(object):
	def __init__(self,conf):
		self.conf = conf

		self.hostname = self.conf.rabbit_host
		self.port = self.conf.rabbit_port
		self.userid = self.conf.rabbit_username
		self.password = self.conf.rabbit_password

		self.connection = kombu.connection.BrokerConnection(hostname=self.hostname,
								    userid=self.userid,
                                                                    password=self.password
								    port=self.port)	
		self.connection.connect()
		self.channel = self.connection.channel()
	def publisher_send(self,cls,topic,msg,timeout):
		publisher=cls(self.conf,self.channel,topic)
		publisher.send(msg,timeout)
	def topic_send(self,topic,msg,timeoute=None):
		self.publisher_send(TopicPublisher,topic,msg,timeout)

	def close(self):
		self.connection.close()

def get_connection_pool(conf):
	return Pool(conf,Connection)
