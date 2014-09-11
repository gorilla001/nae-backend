from sqlalchemy import *
from sqlalchemy.orm import *



class DBAPI():
	def __init__(self):
		self.engine = create_engine(CONF.connection)
		self.connection = self.engine.connect()
	def _execute(self,cmd):
		result=self.connection.execute(cmd)
		self.connection.close()
		return result
	def get_containers(self):
		result=self._execute("select * from containers")
		return result
	def get_container_by_id(self,id):
		result=self._execute("select * from containers where id={}".format(id))
		return result
	def delete_container_by_id(self,id):
		result=self._execute("delete from containers where id={}".format(id))
		return result
