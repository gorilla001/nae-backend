import kombu

class Publisher(object):
	def __init__(self,channel,exchange_name,routing_key,type):
		self.exchange_name = exchange_name
		self.routing_key = routing_key
		self.type=type
		self.channel = channel
		self.exchange = kombu.entity.Exchange(name=self.exchange_name,type=self.type)
		self.producer = kombu.messaging.Producer(exchange=self.exchange,channel=self.channel,routing_key=self.routing_key)
	def send(self,msg,timeout=None):
		self.producer.publish(msg)
		
class TopicPublisher(Publisher):
	def __init__(self,conf,channel,topic):
		exchange_name='docker'
		super(TopicPublisher,self).__init__(channel,exchange_name,topic,type='topic')


