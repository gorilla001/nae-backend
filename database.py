from sqlalchemy import *
from sqlalchemy.orm import *



class DBAPI():
    def __init__(self):
        self.engine = create_engine('mysql://root:root@localhost:3306/jaecpn',convert_unicode=True)
        self.metadata=MetaData(self.engine)
        #self.engine.echo=True
    def add_image(self,image_id='',image_name='',image_size='',image_desc='',image_project='',image_hgs='',image_created='',created_by='',status=''):
        table=Table('images',self.metadata,autoload=True) 
        i=table.insert()
        i.execute(ImageId=image_id,
                  ImageName=image_name,
                  ImageSize=image_size,
                  ImageDesc=image_desc,
                  ProjectID=image_project,
                  ImageHgs=image_hgs,
                  CreatedTime=image_created,
                  CreatedBy=created_by,
                  Status = status,
                  )
    def update_image(self,image_name,image_id='',image_size='',image_desc='',image_project='',image_hgs='',image_created='',created_by='',status=''):
           # Column('ID',Integer,primary_key=True,autoincrement=True),
           # Column('ImageId',String(30)),
           # Column('ImageName',String(50)),
           # Column('ImageSize',String(50)),
           # Column('ImageDesc',String(300)),
           # Column('ProjectID',String(300)),
           # Column('CreatedTime',String(150)),
           # Column('CreatedBy',String(30)),
           # Column('Status',String(100)),

        table=Table('images',self.metadata,autoload=True) 
        u=table.update().where(table.c.ImageName == image_name).values(ImageId = image_id,ImageSize = image_size,ImageHgs = image_hgs,CreatedTime = image_created,Status = status)
        u.execute() 
    def get_images(self,project_id=None):
        table=Table('images',self.metadata,autoload=True) 
        s=table.select()
        if project_id is not None:
            s=table.select(table.c.ProjectID == project_id)
        r=s.execute() 
        return r
    def get_image_by_hgs(self,hgs):
        table=Table('images',self.metadata,autoload=True)
        s=table.select(table.c.ImageHgs == hgs)
        r=s.execute()
        return r
    def delete_image(self,image_id):
        table=Table('images',self.metadata,autoload=True)
        d=table.delete(table.c.ImageName == image_id)
        d.execute()
    def add_container(self,container_id,container_name,container_env,project_id,container_hgs,container_code,access_method,created,created_by,status):
        table=Table('containers',self.metadata,autoload=True)
        i=table.insert()
        i.execute(
                ContainerID = container_id,
                ContainerName = container_name,
                ContainerEnv = container_env,
                ProjectID = project_id,
                Hgs = container_hgs,
                Code = container_code,
                AccessMethod = access_method,
                Created = created,
                CreatedBy = created_by,
                Status = status,
                )
    def get_containers(self):
        table = Table('containers',self.metadata,autoload=True)
        s=table.select()
        r=s.execute()
        return r
    def delete_container(self,container_name):
        table=Table('containers',self.metadata,autoload=True)
        d=table.delete(table.c.ContainerName == container_name)
        d.execute()
    def get_projects(self,project_id=None):
        table=Table('projects',self.metadata,autoload=True)
        s=table.select()
        if project_id is not None:
            s=table.select(table.c.ProjectID == project_id)
        r=s.execute()
        return r
    def add_project(self,project_name,project_hgs,project_admin,project_members,project_desc,created_time):
        table=Table('projects',self.metadata,autoload=True)
        i=table.insert()
        result=i.execute(
                ProjectName=project_name,
                ProjectDesc=project_desc,
                ProjectHgs=project_hgs,
                ProjectAdmin=project_admin,
                ProjectMembers=project_members,
                CreatedTime=created_time,
                )
        return result.lastrowid  
    def update_project(self,project_id,project_name=None,project_hgs=None,project_imgs=None,project_admin=None,project_members=None,project_desc=None):
        #table=Table('projects',self.metadata,autoload=True)
        #u=table.update(table.c.ProjectID == project_id)
        pass
        
    def delete_project(self,project_id):
        table=Table('projects',self.metadata,autoload=True)
        d=table.delete(table.c.ProjectID == project_id)
        d.execute()
    def get_users(self,project_id=None):
        table=Table('users',self.metadata,autoload=True)
        s=table.select()
        if project_id is not None:
            s=table.select(table.c.ProjectID == project_id)
        r=s.execute()
        return r
    def add_user(self,user_id,user_name,project_id,created):
        table=Table('users',self.metadata,autoload=True) 
        i=table.insert()
        i.execute(
                UserID=user_id,
                Name=user_name,
                ProjectID=project_id,
                Created=created
                )



if __name__ == '__main__':
    engine = create_engine('mysql://root:root@localhost:3306/jaecpn')
    metadata = MetaData(engine)

    images_table = Table('images',metadata,
            Column('ID',Integer,primary_key=True,autoincrement=True),
            Column('ImageId',String(30)),
            Column('ImageName',String(50)),
            Column('ImageSize',String(50)),
            Column('ImageDesc',String(300)),
            Column('ProjectID',String(300)),
            Column('ImageHgs',String(300)),
            Column('CreatedTime',String(150)),
            Column('CreatedBy',String(30)),
            Column('Status',String(100)),
    )

    projects_table = Table('projects',metadata,
            Column('ProjectID',Integer,primary_key=True,autoincrement=True),
            Column('ProjectName',String(50)),
            Column('ProjectDesc',String(300),default=''),
            Column('ProjectHgs',String(500)),
            Column('ProjectImgs',String(500),default=''),
            Column('ProjectAdmin',String(30)),
            Column('ProjectMembers',String(500),default=''),
            Column('CreatedTime',String(150)),
    )

    #users_table = Table('users',metadata,
    #        Column('Id',Integer,primary_key=True,autoincrement=True),
    #        Column('Name',String(30)),
    #        Column('UserName',String(30)),
    #        Column('DepartMent',String(30)),
    #        Column('Email',String(30)),
    #        Column('Created',String(30)),
    #)
    users_table = Table('users',metadata,
            Column('Id',Integer,primary_key=True,autoincrement=True),
            Column('UserID',String(30)),
            Column('Name',String(30)),
            Column('ProjectID',Integer),
            Column('Created',String(150)),
    )

    containers_table = Table('containers',metadata,
            Column('Id',Integer,primary_key=True,autoincrement=True),
            Column('ContainerID',String(50)),
            Column('ContainerName',String(50)),
            Column('ContainerEnv',String(30)),
            Column('ProjectID',Integer),
            Column('Hgs',String(300)),
            Column('Code',String(300)),
            Column('AccessMethod',String(300)),
            Column('Created',String(150)),
            Column('CreatedBy',String(30)),
            Column('Status',String(100)),
    )
    hgs_table = Table('hgs',metadata,
            Column('Id',Integer,primary_key=True,autoincrement=True),
            Column('ProjectID',Integer),
            Column('ImageID',Integer),
    )


    engine.echo=True
    images_table.create(checkfirst=True)
    projects_table.create(checkfirst=True)
    users_table.create(checkfirst=True)
    containers_table.create(checkfirst=True)
    hgs_table.create(checkfirst=True)
    print 'ok'
