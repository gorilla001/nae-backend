from sqlalchemy import *
from sqlalchemy.orm import *



class DBAPI():
    def __init__(self):
        self.engine = create_engine('mysql://root:root@localhost:3306/jaecpn')
        self.metadata=MetaData(self.engine)
        self.engine.echo=True
    def insert(self,table):
        table=Table(table,self.metadata,autoload=True) 
        i=table.insert()
        i.execute()


if __name__ == '__main__':
    engine = create_engine('mysql://root:root@localhost:3306/jaecpn')
    metadata = MetaData(engine)

    images_table = Table('images',metadata,
            Column('ImageId',String(30)),
            Column('ImageName',String(50)),
            Column('ImageSize',String(50)),
            Column('ImageDesc',String(300)),
            Column('CreatedTime',String(150)),
            Column('CreatedBy',String(30)),
    )

    engine.echo=True
    images_table.create()
    print 'ok'
