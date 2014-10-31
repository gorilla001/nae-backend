from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.sql import and_
from sqlalchemy.sql import func,select


DATABASE_URL="mysql://jaecpn:jaecpn@localhost/jaecpn"

class DBAPI():
    def __init__(self):
        self.engine = create_engine(DATABASE_URL,convert_unicode=True)
        self.metadata=MetaData(self.engine)
        #self.engine.echo=True
    def add_image(self,name,tag,desc,project_id,repo,branch,created,owner,status,image_id=None,size=None):
        table=Table('images',self.metadata,autoload=True) 
        i=table.insert()
        result=i.execute(
                  ImageName=name,
		  ImageTag=tag,
                  ImageDesc=desc,
                  ProjectID=project_id,
                  RepoPath=repo,
		  Branch = branch,
                  Created=created,
                  Owner=owner,
                  Status = status,
                  )
        return result.lastrowid  
    def update_image(self,id,image_id,size,status):
        table=Table('images',self.metadata,autoload=True) 
        u=table.update().where(table.c.ID == id).values(ImageId = image_id,ImageSize =size,Status = status)
        u.execute() 
    def update_image_status(self,id,status):
        table=Table('images',self.metadata,autoload=True) 
        u=table.update().where(table.c.ID == id).values(Status = status)
        u.execute() 
    def update_image_id(self,_id,image_id):
        table=Table('images',self.metadata,autoload=True) 
        u=table.update().where(table.c.ID == _id).values(ImageId = image_id)
        u.execute() 
    def commit_image(self):
	pass

    def get_images(self,project_id=None):
        table=Table('images',self.metadata,autoload=True) 
        s=table.select()
        if project_id is not None:
            s=table.select(table.c.ProjectID == project_id)
        r=s.execute() 
        return r
    def get_image(self,image_id):
        table=Table('images',self.metadata,autoload=True)
        s=table.select(table.c.ID == image_id)
        return s.execute()
    def get_image_by_id(self,image_id):
        table=Table('images',self.metadata,autoload=True)
        s=table.select(table.c.ID == image_id)
        r=s.execute()
        return r
    def get_image_by_hgs(self,hgs):
        table=Table('images',self.metadata,autoload=True)
        s=table.select(table.c.ImageHgs == hgs)
        r=s.execute()
        return r
    def delete_image(self,image_id):
        table=Table('images',self.metadata,autoload=True)
        d=table.delete(table.c.ID == image_id)
        d.execute()
    def delete_images(self,project_id):
        table=Table('images',self.metadata,autoload=True)
        d=table.delete(table.c.ProjectID == project_id)
        return d.execute()

    def add_container(self,container_name,container_env,project_id,container_hg,container_code,container_image,created,created_by,status,container_id=None,access_method=None):
        table=Table('containers',self.metadata,autoload=True)
        i=table.insert()
        result=i.execute(
                ContainerName = container_name,
                ContainerEnv = container_env,
                ProjectID = project_id,
                Hgs = container_hg,
                Code = container_code,
		Image = container_image,
                Created = created,
                CreatedBy = created_by,
                Status = status,
                )
        return result.lastrowid  
    def update_container(self,id,container_id,status):
        table=Table('containers',self.metadata,autoload=True) 
        u=table.update().where(table.c.Id == id).values(ContainerID = container_id,Status = status)
        u.execute() 

    def update_container_status(self,id,status):
        table=Table('containers',self.metadata,autoload=True) 
        u=table.update().where(table.c.Id == id).values(Status = status)
        u.execute() 
    def update_container_network(self,id,network):
        table=Table('containers',self.metadata,autoload=True) 
        u=table.update().where(table.c.Id == id).values(AccessMethod = network)
        u.execute() 
    def get_containers(self,project_id,user_id):
        table = Table('containers',self.metadata,autoload=True)
        s = table.select().where(and_(
                                    table.c.ProjectID == project_id,
                                    table.c.CreatedBy == user_id)
                                    ).order_by(table.c.Id)

        return s.execute() 
    def get_container(self,container_id):
        table=Table('containers',self.metadata,autoload=True)
        s=table.select(table.c.Id == container_id)
        return s.execute()
    def get_container_count(self,container_name):
        table=Table('containers',self.metadata,autoload=True)
        s=table.select(table.c.ContainerName == container_name)
        return len(s.execute().fetchall())
    def delete_container(self,container_id):
        table=Table('containers',self.metadata,autoload=True)
        d=table.delete(table.c.Id == container_id)
        d.execute()
    def delete_containers(self,project_id):
        table=Table('containers',self.metadata,autoload=True)
        d=table.delete(table.c.ProjectID == project_id)
        return d.execute()
    def get_max_container_id(self):
        table=Table('containers',self.metadata,autoload=True)
        s=select([func.max(table.c.Id)])
        return s.execute()

    def get_projects(self):
        table=Table('projects',self.metadata,autoload=True)
        s=table.select()
        r=s.execute()
        return r
    def get_project_by_id(self,project_id):
        table=Table('projects',self.metadata,autoload=True)
        s=table.select(table.c.ProjectID == project_id)
        return s.execute()
    def get_project(self,project_id):
        table=Table('projects',self.metadata,autoload=True)
        s=table.select(table.c.ProjectID == project_id)
        return s.execute()
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
        table=Table('projects',self.metadata,autoload=True)
        u=table.update().\
            where(table.c.ProjectID == project_id).\
            values(ProjectName = project_name,
                    ProjectDesc = project_desc,
                    ProjectMembers = project_members,
                    ProjectHgs = project_hgs)
        return u.execute()
        
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
    def get_project_id_by_user_id(self,user_id):
        table=Table('users',self.metadata,autoload=True)
        s=table.select(table.c.UserID == user_id)
        return s.execute()

    def show_project(self,project_id):
        table=Table('projects',self.metadata,autoload=True)
        s=table.select(table.c.ProjectID == project_id)
        return s.execute()
        
    def add_user(self,user_id,user_email,project_id,role_id,created,user_name=None):
        table=Table('users',self.metadata,autoload=True) 
        i=table.insert()
        i.execute(
                UserID=user_id,
                Email = user_email,
                Name=user_name,
                ProjectID=project_id,
                RoleID = role_id,
                Created=created
                )
    def delete_user(self,id):
        table = Table('users',self.metadata,autoload=True)
        d=table.delete(table.c.Id == id)
        return d.execute()

    def delete_users(self,project_id):
        table = Table('users',self.metadata,autoload=True)
        d=table.delete(table.c.ProjectID == project_id)
        d.execute()
    def user_exist(self,project_id,user_id):
        table = Table('users',self.metadata,autoload=True)
        s = table.select().where(and_(
                                    table.c.ProjectID == project_id,
                                    table.c.UserID == user_id)
                                    )
        r = s.execute().fetchone()
        if r is not None:
            return True
        return False
    def add_hg(self,project_id,hg_addr,created):
        table=Table('hgs',self.metadata,autoload=True)
        i=table.insert()
        i.execute(
                ProjectID = project_id,
                Content = hg_addr,
                Created = created,
                )
    def delete_hg(self,hg_id):
        table = Table('hgs',self.metadata,autoload=True)
        d=table.delete(table.c.Id == hg_id)
        return d.execute()

    def get_hg(self,image_id):
        table=Table('hgs',self.metadata,autoload=True)
        s=table.select(table.c.ImageID == image_id)
        return s.execute()
    def get_hgs(self,project_id):
        table=Table('hgs',self.metadata,autoload=True)
        s=table.select(table.c.ProjectID == project_id)
        return s.execute()
    def delete_hgs(self,project_id):
        table=Table('hgs',self.metadata,autoload=True)
        d=table.delete(table.c.ProjectID == project_id)
        return d.execute()

    def add_sftp(self,container_id,sftp_addr,sftp_user,sftp_port=22):
        table=Table('sftp',self.metadata,autoload=True)
        i=table.insert()
        i.execute(
                ContainerID = container_id,
                Sftp = sftp_addr,
                User = sftp_user,
                Port = sftp_port,
                )
    def get_sftp(self,container_id):
        table=Table('sftp',self.metadata,autoload=True)
        d=table.select(table.c.ContainerID == container_id)
        return d.execute()
    def add_network(self,container_id,pub_host,pub_port,pri_host,pri_port):
        table=Table('networks',self.metadata,autoload=True)
        i=table.insert()
        i.execute(
                ContainerID = container_id,
                PublicHost = pub_host,
                PublicPort = pub_port,
                PrivateHost = pri_host,
                PrivatePort = pri_port,
                )
    def get_network(self,container_id):
        table=Table('networks',self.metadata,autoload=True)
        s=table.select(table.c.ContainerID == container_id)
        return s.execute()







if __name__ == '__main__':
    engine = create_engine('mysql://jaecpn:jaecpn@localhost:3306/jaecpn')
    metadata = MetaData(engine)

    images_table = Table('images',metadata,
            Column('ID',Integer,primary_key=True,autoincrement=True),
            Column('ImageId',String(30)),
            Column('ImageName',String(50)),
	    Column('ImageTag',String(50)),
            Column('ImageSize',String(50)),
            Column('ImageDesc',String(300)),
            Column('ProjectID',String(300)),
            Column('RepoPath',String(300)),
            Column('Branch',String(150)),
            Column('Created',String(150)),
            Column('Owner',String(30)),
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
            Column('Email',String(150)),
            Column('Name',String(30)),
            Column('ProjectID',Integer),
            Column('RoleID',Integer),
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
            Column('Image',String(300)),
            Column('AccessMethod',String(300)),
            Column('Created',String(150)),
            Column('CreatedBy',String(30)),
            Column('Status',String(100)),
    )
    hgs_table = Table('hgs',metadata,
            Column('Id',Integer,primary_key=True,autoincrement=True),
            Column('Content',String(300)),
            Column('ProjectID',Integer),
            Column('Created',String(150)),
    )

    #sftp_table = Table('sftp',metadata,
    #        Column('Id',Integer,primary_key=True,autoincrement=True),
    #        Column('ContainerID',String(50)),
    #        Column('Sftp',String(100)),
    #        Column('User',String(30)),
    #        Column('Port',String(30)),
    #)
    network_table = Table('networks',metadata,
            Column('Id',Integer,primary_key=True,autoincrement=True),
            Column('ContainerID',String(50)),
            Column('PublicHost',String(100)),
            Column('PublicPort',String(30)),
            Column('PrivateHost',String(100)),
            Column('PrivatePort',String(30)),
   )



    engine.echo=True
    images_table.create(checkfirst=True)
    projects_table.create(checkfirst=True)
    users_table.create(checkfirst=True)
    containers_table.create(checkfirst=True)
    hgs_table.create(checkfirst=True)
    #sftp_table.create(checkfirst=True)
    network_table.create(checkfirst=True)

