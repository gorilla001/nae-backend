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
    def get_projects(self):
        table=Table('projects',self.metadata,autoload=True)
        s=table.select()
        r=s.execute()
        return r
    def add_project(self,project_name,project_image,project_admin,project_desc,created_time,created_by):
        table=Table('projects',self.metadata,autoload=True)
        i=table.insert()
        i.execute(
                ProjectName=project_name,
                ProjectDesc=project_desc,
                ProjectImage=project_image,
                ProjectAdmin=project_admin,
                CreatedTime=created_time,
                CreatedBy=created_by,
                )
        print 'image:',project_image
    def get_users(self):
        table=Table('users',self.metadata,autoload=True)
        s=table.select()
        r=s.execute()
        return r
    def add_user(self,user_name,cn_name,department,email,created):
        table=Table('users',self.metadata,autoload=True) 
        i=table.insert()
        i.execute(Name=user_name,UserName=cn_name,DepartMent=department,Email=email,Created=created)



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

    projects_table = Table('projects',metadata,
            Column('ProjectID',Integer,primary_key=True,autoincrement=True),
            Column('ProjectName',String(50)),
            Column('ProjectDesc',String(300),default=''),
            Column('ProjectImage',String(50)),
            Column('ProjectAdmin',String(30)),
            Column('ProjectMembers',String(500)),
            Column('CreatedTime',String(150)),
            Column('CreatedBy',String(150)),
    )

    users_table = Table('users',metadata,
            Column('Id',Integer,primary_key=True,autoincrement=True),
            Column('Name',String(30)),
            Column('UserName',String(30)),
            Column('DepartMent',String(30)),
            Column('Email',String(30)),
            Column('Created',String(30)),
    )


    engine.echo=True
    images_table.create(checkfirst=True)
    projects_table.create(checkfirst=True)
    users_table.create(checkfirst=True)
    print 'ok'
