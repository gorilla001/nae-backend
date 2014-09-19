from sqlalchemy import *
from sqlalchemy.orm import *



class DBAPI():
    def __init__(self):
        self.engine = create_engine('mysql://root:root@localhost:3306/jaecpn',convert_unicode=True)
        self.metadata=MetaData(self.engine)
        self.engine.echo=True
    def insert_image(self,image_id,image_name,image_size,image_desc,image_created,created_by):
        table=Table('images',self.metadata,autoload=True) 
        i=table.insert()
        #i=table.insert(
        #        ImageId=image_id,
        #        ImageName=image_name,
        #        ImageSize=image_size,
        #        ImageDesc=image_desc,
        #        CreatedTime=image_created,
        #        CreatedBy=created_by
        #        )
        i.execute(ImageId=image_id,ImageName=image_name,ImageSize=image_size,ImageDesc=image_desc,CreatedTime=image_created,CreatedBy=created_by)
    def select_images(self):
        table=Table('images',self.metadata,autoload=True) 
        s=table.select()
        r=s.execute() 
        return r


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
