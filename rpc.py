import pools


class RPCAPI(object):
	def __init__(self):
		self.pool=pools.get_connection_pool()
	def cast(self,context,topic,msg):
		with self.pool.get() as conn:
			connection.topic_send(context,topic,msg)
	def call(self.context,topic,msg):
		with self.pool.get() as conn:
			connection.topic_send(context,topic,msg)
