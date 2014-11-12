from  session import get_session
import models


def model_query(model):
    model = model
    session = get_session()
    with session.begin():
        query = session.query(model)

    return query

def add_image(values):
    session = get_session()
    with session.begin():
	model=models.Image()
	model.update(values)
	model.save(session=session)	

def get_images(project_id):
    model = models.Image
    query = model_query(model) \ 
            .filter_by(ProjectID=project_id)

    return query.all()

def get_image(img_id):
    model = models.Image
    query = model_query(model) \
            .filter_by(ID=img_id)

    return query.first()

def update_image(_id,img_id):
    session = get_session()
    with session.begin():
        query = session.query(self.model)
        query = query.filter_by(ProjectID=project_id)
    return query.all()


def delete_image(img_id):
    model = models.Image
    query = model_query(model) \
        .filter_by(ID=img_id) 

    return query.delete() 


def add_container(values):
    session = get_session()
    with session.begin():
        model=models.Container()
        model.update(values)
        model.save(session=session)

def update_container():
    session = get_session()
    with session.begin():
        pass

def update_container_status(model=models.Container,status):
    model = models.Container
    query = model_query()
 
def update_container_network():
    session = get_session()
    with session.begin():
        pass

def get_containers(model=models.Container,project_id):
    session = get_session()
    with session.begin():
        query = session.query(model) \
                .filter_by(ProjectID=project_id)
    return query.all()

def get_container(model=models.Container,id):
    session = get_session()
    with session.get_session():
        query = session.query(model) \
                .filter_by(ID=id)

    return query.first()

def get_container_status():
def get_container_count():
def delete_container():
    session = get_session()
    with session.get_session():
        query = session.query(model) \
                .filter_by(ID=id)
    return query.delete()

def delete_containers():
def get_max_container_id():

def get_projects():
    model = models.Container
    session = get_session()
    with session.begin():
        pass

def get_project_by_id():
    model = models.Container
    session = get_session()
    with session.begin():
        pass

def get_project():
def add_project():
def update_project():
def delete_project():

def add_user():
def delete_user():
def delete_users(): 
def user_exist():

def add_hg():
def delete_hg():
def get_hg():
def get_hgs():
def delete_hgs():

def add_network():
def get_network():
def delete_network():
